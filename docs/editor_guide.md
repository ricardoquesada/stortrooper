# Stortroopers Editor Guide

Stortroopers Editor is a powerful pixel art character creator tool designed to help you build unique characters by combining various assets like bodies, heads, hair, and accessories.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Working with Projects](#working-with-projects)
4. [Creating Characters](#creating-characters)
5. [Exporting](#exporting)
6. [Keyboard Shortcuts](#keyboard-shortcuts)

## Getting Started

To launch the editor, run the following command in your terminal:

```bash
make run
```

This will open the main window where you can start creating characters immediately.

## Interface Overview

The editor interface consists of three main areas:

1.  **Canvas (Center):** This is your workspace where the character is assembled. You can see your changes in real-time.
2.  **Tools Panel (Right):** Contains controls for selecting characters and a list of available assets organized by category.
3.  **Main Toolbar (Top):** Provides quick access to common actions like saving, opening, and modifying the character.

### Tools Panel

-   **Character Type:** Dropdown to select the base style of the character (e.g., Boy, Girl, Robot).
-   **Articles File:** Selects the specific data file defining available assets for the chosen character type.
-   **Asset Categories:** A scrollable list of collapsible categories (e.g., **Body**, **Head**, **Hair**, **Tops**). Click the arrow or title to expand/collapse a category.
-   **Asset List:** Inside each category, icons represent available items.

### Main Toolbar

The toolbar at the top provides buttons for:
-   **File Operations:** Open, Save, Save As, Export.
-   **Random:** Generates a completely random character.
-   **Change Outfit:** Randomizes clothes and accessories while keeping the body and head (identity) intact.
-   **Tinting:** Tools to colorize specific items (see [Tinting Items](#tinting-items)).
-   **Zoom:** Zoom In/Out.

## Working with Projects

A "Project" (`.stp` or `.json` file) saves the current configuration of your character (selected assets, positions, and tints).

-   **New Project:** Creates a fresh, empty workspace in a new tab.
-   **Open Project:** Loads a previously saved project file.
-   **Open Recent:** Quickly access your most recently opened files from the File menu.
-   **Save Project:** Saves your current progress.
-   **Save Project As:** Save the current project to a new file location.
-   **Restore Default Layout:** If you lose a dock or toolbar, use **Window > Restore Default Layout** to reset the interface.

> **Note:** The editor restores your last session (open tabs and window state) automatically when you reopen it.

## Creating Characters

1.  **Select a Character Type:** Use the "Character Type" dropdown in the Tools panel.
2.  **Browse Assets:** Expand categories in the Tools panel to view available items.
3.  **Add Assets:** Click an icon to add it to your character.
    -   Active assets are highlighted in **Cyan**.
    -   Clicking a different asset in the same layer replaces the previous one.
4.  **Remove Assets:** Click an already active (cyan) asset to remove it.

### Randomization

-   **Random:** Randomizes everything, including character base, specific articles file, and all outfit pieces.
-   **Change Outfit:** Keeps the current character base (Body, Head) but randomizes clothing (Tops, Bottoms, Shoes, etc.).

### Tinting Items

You can apply a color tint to any selected item.

1.  **Select an Item:** Click an asset in the Tools panel so it is active (cyan).
2.  **Tint:** Click the **Tint Active Item** button in the toolbar (or press `Ctrl+T`). A color picker will appear. Select a color to apply it.
3.  **Reset Tint:** To remove the color, select the item and click **Reset Tint** (or press `Ctrl+Shift+T`).

## Exporting

Once you are happy with your character, you can export it as an image.

1.  Click the **Export to PNG** button in the toolbar, or select **File > Export to PNG...**.
2.  Choose a destination and filename.
3.  The character will be saved as a transparent PNG image.

## Keyboard Shortcuts

| Action | Shortcut |
| :--- | :--- |
| **New Project** | `Ctrl + N` |
| **Open Project** | `Ctrl + O` |
| **Save Project** | `Ctrl + S` |
| **Save Project As** | `Ctrl + Shift + S` |
| **Export to PNG** | `Ctrl + E` |
| **Close Tab** | `Ctrl + W` |
| **Tint Active Item** | `Ctrl + T` |
| **Reset Tint** | `Ctrl + Shift + T` |
| **Zoom In** | `Ctrl + +` |
| **Zoom Out** | `Ctrl + -` |
