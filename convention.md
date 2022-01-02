Due to require from our teachers, we can not use Javascript, so we use Python.

# Convention

## 1. Naming

- Variable name: **camelCase**
- Function name : **camelCase**, action in **lowercase** and noun in **UPPERCASE**.
- Global variable name: **UPPERCASE**
- Constant (such as PI): **UPPERCASE**
- File name: **lowercase** (may be mix with "-" or "\_")

## 2. Parameters

- Parameters name: **camelCase**
- Maximum parameters is **5**

## 3. Line Lenght **< 80** (column **< 80**)

## 4. Block of code

- Always end a block of code with semicolon (even unesscarry)
- Seperate two block of code by a blank space

By the way, we can use Prettier extension in VS Code for code formatting

# Source Code Organization

All of code will be in **src** folder.  
All of images will be in **imgs** folder.
Database will be in **db** folder
Beside, we will have a **release** folder cointaining executable file.
Also, we also have a **report file** in PDF format.

# Git

## Commit Message

Should be short, such as a formula like this:

`do + something + in some file`

Example:

`update convention in readme.md`

## Branch

Whenever a member has a new feature to do, he must create a new branch with that feature name. Until the next meeting, he can not merge that branch into main branch.

## Pull

If somebody has conflict with the code between local repository and global repository, he have to make a pull request from global repository and modify his local repository first. Then, after resolving, he can push those changes to global repository.
