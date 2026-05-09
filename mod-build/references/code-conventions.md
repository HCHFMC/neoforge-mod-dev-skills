# Minecraft Mod Code Conventions

## Core Coding Standards

### NEVER Trust Memory
Every API signature, class path, and method name must come from one of:
- **L1**: Code that achieved BUILD SUCCESS in this NeoForge version
- **L2**: JAR decompilation with `javap` on neo-21.0.167.jar
- **L3**: `raw/framework-tests/` — NeoForge official test code
- **L4**: `raw/neoforge-docs/version-1.21.1/` — official documentation

**Never** generate NeoForge API calls from LLM training data. This caused 6 compilation errors in early development.

### Proven API Problems (NeoForge 21.0.167)

These are the API signatures that differ from LLM training data expectations:

| What LLMs Generate | Actual API | Source |
|-------------------|-----------|--------|
| `new BlockEntityType<>(factory, false, block)` | `new BlockEntityType<>(factory, Set.of(block), null)` | JAR javap |
| `loadAdditional(ValueInput)` | `loadAdditional(CompoundTag, HolderLookup.Provider)` | Compile test |
| `import org.jspecify.annotations.Nullable` | Not available in standard dependencies | Compile test |
| `addStandardInventorySlots(inv, x, y)` | Method does not exist; add Slot manually | Compile test |
| `appendHoverText(stack, ctx, display, Consumer<Component>, flag)` | `appendHoverText(stack, ctx, List<Component>, flag)` | JAR javap |
| `SimpleMenuProvider` for opening menu from item | Use `MenuProvider` anonymous class + `ItemStack.OPTIONAL_STREAM_CODEC` | Mod reference |

### Code Style

```
Naming:
  - Class names: PascalCase (SolarPanelBlock)
  - Methods: camelCase (canGenerate, getEnergyStored)
  - Constants: SCREAMING_SNAKE_CASE (MODID, MAX_CAPACITY)
  - Package: lowercase, no underscores (com.solarmod.blockentity)

Mappings:
  - Use Parchment mappings (human-readable parameter names)
  - e.g., BlockBehaviour.Properties.of().strength(3f).sound(SoundType.METAL)

Imports:
  - Always include ALL imports in code blocks
  - Never use wildcard imports (import net.minecraft.world.level.block.*)
```

## Pattern Usage Rules

### When to Copy a Pattern
```
1. KB pattern exists that covers the feature → copy pattern
2. Override ONLY ★-marked customization points
3. Keep all other code identical to the pattern

Example:
  energy-generator pattern → copy entire 150-line BlockEntity
  → Override: canGenerate() (3 lines)
  → Keep: tick(), pushEnergy(), IEnergyStorage (147 lines unchanged)
```

### When to Write Custom Code
```
1. No KB pattern exists for this feature type
2. The closest pattern covers <50% of what's needed
3. The customization would touch >30% of the pattern code
→ In this case, write the new code and FILE BACK as a new pattern
```

## Registration Patterns

### Block + BlockEntity + Menu (Standard Machine)

```java
// In SolarMod.java:

// 1. Registration
public static final DeferredBlock<MyBlock> MY_BLOCK = BLOCKS.register("my_id",
    () -> new MyBlock(BlockBehaviour.Properties.of()
        .strength(3f).requiresCorrectToolForDrops().sound(SoundType.METAL)));

public static final DeferredItem<BlockItem> MY_ITEM = ITEMS.registerSimpleBlockItem(MY_BLOCK);

public static final Supplier<BlockEntityType<MyBlockEntity>> MY_BE = BLOCK_ENTITIES.register("my_id",
    () -> new BlockEntityType<>(MyBlockEntity::new, Set.of(MY_BLOCK.get()), null));

public static final Supplier<MenuType<MyMenu>> MY_MENU = MENUS.register("my_id",
    () -> IMenuTypeExtension.create(MyMenu::new));

// 2. Creative tab (in static block)
output.accept(MY_ITEM.get());

// 3. Capability registration (in registerCapabilities)
event.registerBlockEntity(Capabilities.EnergyStorage.BLOCK, MY_BE.get(), (be, side) -> be);

// 4. Screen registration (in ClientModEvents)
event.register(MY_MENU.get(), MyScreen::new);
```

### Config Entry

```java
// In Config.java — add BEFORE "static final ModConfigSpec SPEC = BUILDER.build();"

public static final ModConfigSpec.IntValue MY_GENERATION = BUILDER
    .comment("Description of this config")
    .defineInRange("configKey", defaultValue, minValue, Integer.MAX_VALUE);
```

## IEnergyStorage Implementation

The verified implementation (6 methods):

```java
// All 6 methods required. These are the exact signatures for NeoForge 21.0.167.

@Override
public int receiveEnergy(int maxReceive, boolean simulate) {
    int received = Math.min(capacity - energy, maxReceive);
    if (!simulate) { energy += received; setChanged(); }
    return received;
}

@Override
public int extractEnergy(int maxExtract, boolean simulate) {
    int extracted = Math.min(energy, Math.min(maxExtract, transferRate));
    if (!simulate) { energy -= extracted; setChanged(); }
    return extracted;
}

@Override public int getEnergyStored() { return energy; }
@Override public int getMaxEnergyStored() { return capacity; }
@Override public boolean canExtract() { return energy > 0; }
@Override public boolean canReceive() { return energy < capacity; }

// Energy push pattern (in tick or pushEnergy method):
for (Direction dir : Direction.values()) {
    IEnergyStorage target = level.getCapability(
        Capabilities.EnergyStorage.BLOCK, worldPosition.relative(dir), dir.getOpposite());
    if (target != null && target.canReceive()) {
        int extracted = extractEnergy(transferRate, true);
        if (extracted > 0) {
            int accepted = target.receiveEnergy(extracted, false);
            if (accepted > 0) extractEnergy(accepted, false);
        }
    }
}
```

## Menu / ContainerData Pattern

### Stale Data Bug Fix (Critical)
SimpleContainerData created at menu construction time is a SNAPSHOT. It does NOT auto-sync. You MUST:

```java
// 1. Store BE reference
private final MyBlockEntity be; // null on client-side

// 2. Override broadcastChanges() to refresh from BE before syncing
@Override
public void broadcastChanges() {
    if (be != null) {
        ((SimpleContainerData) data).set(0, be.getEnergyStored());
        ((SimpleContainerData) data).set(1, be.getMaxEnergyStored());
        ((SimpleContainerData) data).set(2, be.isGenerating() ? 1 : 0);
    }
    super.broadcastChanges();
}
```

### Adding Player Inventory Slots (Manual)
```java
// 9×3 main inventory
for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 9; ++j) {
        this.addSlot(new Slot(playerInv, j + i * 9 + 9, 8 + j * 18, 84 + i * 18));
    }
}
// 1×9 hotbar
for (int k = 0; k < 9; ++k) {
    this.addSlot(new Slot(playerInv, k, 8 + k * 18, 142));
}
```

## NBT Persistence

```java
// Verified signatures for NeoForge 21.0.167:

@Override
protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
    super.saveAdditional(tag, registries);           // MANDATORY
    tag.putInt("energy", energy);
    tag.put("upgrades", inventory.serializeNBT(registries));
}

@Override
protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
    super.loadAdditional(tag, registries);           // MANDATORY
    energy = tag.getInt("energy");
    if (tag.contains("upgrades")) {
        inventory.deserializeNBT(registries, tag.getCompound("upgrades"));
    }
}

// Always call setChanged() after modifying persistent fields
```
