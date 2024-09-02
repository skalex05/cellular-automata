# Cellular Automata
![Screenshot 2024-08-31 1427482.png](Images%2FScreenshot%202024-08-31%201427482.png)
## What are Cellular Automata?

This software can be used to simulate deterministic 2D Grid **Cellular Automata**. 

These **Cellular Automata** consist of a square grid occupied by *cells* which may exist in *two states*. **Alive** or **Dead**.

The state of each cell is determined by a fixed set of rules:
- **A Neighbourhood**
- **A Survival Condition**
- **A Birth Condition**

The *birth* and *survival* conditions are determined true if a cell has a particular number of living neighbours in its *neighbourhood*.

The most well known cellular automata must be **John Conway's Game Of Life**. The rules for these cellular automata are:

- **A Moore Neighbourhood** (All eight directly neighbouring cells in a 2D grid of squares)
- A cell survives *if it has either two or three neighbours*
- A cell is born *if it has exactly three neighbours*

From the first time I was introduced to cellular automata several years ago I was fascinated by how such simplicity could bring forth such complexity and intricate patterns.

I have often thought of Conway's Game Of Life as the foreshadowing for our own reality in that despite the intricate, unfathomable complexity of our universe, it may be describable by some simple, fundamental axioms. Maybe someday we will have a unified model of the universe.
![Screenshot 2024-09-01 220516.png](Images%2FScreenshot%202024-09-01%20220516.png)
The program defaults to the rules to Game of Life.

## Examples

![Screenshot 2024-08-31 185843.png](Images%2FScreenshot%202024-08-31%20185843.png)
![Screenshot 2024-08-31 185151.png](Images%2FScreenshot%202024-08-31%20185151.png)
![Screenshot 2024-08-31 143851.png](Images%2FScreenshot%202024-08-31%20143851.png)
![Screenshot 2024-08-31 142030.png](Images%2FScreenshot%202024-08-31%20142030.png)
![Screenshot 2024-09-01 212737.png](Images%2FScreenshot%202024-09-01%20212737.png)

## Usage

### Installation
If you would like to explore cellular automata yourself, simply clone this repo to your own machine. 

Next in the terminal, install the required modules by running the following within your local repo:

`pip install -r requirements.txt`

After that, simply run:

`python main.py`

### Interacting with the viewport

![Screenshot 2024-09-01 222616.png](Images%2FScreenshot%202024-09-01%20222616.png)

If all has installed correctly, a window will appear. 

The main **Viewport** is where you can view your cellular automata.

To manually intervene with the world, press your `Left Mouse Button` to make a cell become **alive**.

You may also **kill** cells by pressing the `Right Mouse Button`.

You can **zoom** with `Scroll Wheel`. 

**Pressing the scroll wheel while dragging your mouse** will pan the camera around the viewport. 

The grid consists of *10000 x 10000* cell locations so try not to get lost!

To clear the grid, press `CTRL + R`.

You may pause state changes by pressing `P`.

### Settings

The **Settings Window** is located to the *right* of the **Viewport**. 

It can be **minimised** or **maximised** by pressing the button in the *top left corner* of the **Settings Panel**.

The **Speed** slider can be used to control how many **state transitions per second** cells go through. The perceived effect is the higher the value the faster they will move. 

An FPS counter adjoins this indicating the true number of **state transitions per second**.


![Screenshot 2024-09-01 224251.png](Images%2FScreenshot%202024-09-01%20224251.png)

The **Live If** and **Birth** If conditions are used to determine when a cell *lives/becomes alive* depending on how many **living neighbours** it has **(x)**. The settings above describe the default conditions for **Conway's Game of Life**.

Color properties can also be altered for **cells** and the **background** using **BG Color** and **Cell Color** properties.
A color may either be adjusted by **writing in a particular hexadecimal color code** or by **clicking the preview color** to the *right* of this field. This will display another window that may be easier for individuals to find the exact color they want.

![Screenshot 2024-09-01 223619.png](Images%2FScreenshot%202024-09-01%20223619.png)

Pressing the **Edit Neighbourhood** button in settings will greet you with a central cell surrounded by turquoise **neighbours**. 

A **neighbourhood** may be modified with the **same controls** for creating and deleting cells in the **main viewport**.

- `Left Mouse Button` will **add** a cell to the neighbourhood at the cursor's position.
- `Right Mouse Button` will **remove** a cell from the neighbourhood at the cursor's position.

Once complete, pressing the **Edit Neighbourhood** button will return you to the **viewport**

Settings may be **saved** and **loaded** from `.cas` files. The repository comes with several `.cas` files in the `/Saves` folder. These save files are useful ways to quickly switch between different cellular automata rules and allows you to return to old discoveries later.