# Tokamaker

Tokamaker is a tool for generating hexahedral Tokamak CFD meshes in Gmsh. Additionally, it comes built in with parameters for a few current devices. It uses the specified major and minor radii to construct a D-shaped cross section.

## Usage
Tokamaker is straightforward to use. Make sure Gmsh is installed and simply clone Tokamaker wherever you want to use it and run
```
python3 tokamaker/tokamaker.py
```
You will be asked to enter some parameters and then the mesh will be generated.

## Notes
Currently, the script generates a v2.0 binary Gmsh files with second order quadrangles/hexahedrons. A single physical group, "wall," is defined that represents both the flat internal wall and the arced outer wall. This physical group is normally used to configure boundary conditions.