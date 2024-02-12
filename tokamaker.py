import math
import gmsh

# Tokamak "database" provides parameters for some tokamaks (taken from https://en.wikipedia.org/wiki/List_of_fusion_experiments).
tokamak_database = [
    #Name           major/minor radii
    ["JET",             2.96, 0.96],
    ["DIII-D",          1.67, 0.67],
    ["Alcator C-Mod",   0.68, 0.22],
    ["NSTX",            0.85, 0.68],
    ["ITER",            6.20, 2.00],
    ["SPARC",           1.85, 0.57]
]

r_major     = 0
r_minor     = 0
e_size      = 0
mesh_name   = ""

# Get tokamak parameters
print("===== Tokamaker v1.0.0 =====")
print("Specify tokamak parameters:")
print("\t0: Custom")
for i in range(0, len(tokamak_database)):
    print(f"\t{i + 1}: {tokamak_database[i][0]}")
tokamak_choice = int(input())
if tokamak_choice == 0:
    r_major     = float(input("\tInput major radius in meters: "))
    r_minor     = float(input("\tInput minor radius in meters: "))
else:
    r_major = tokamak_database[tokamak_choice - 1][1]
    r_minor = tokamak_database[tokamak_choice - 1][2]

# Get mesh paramaters
print("Specify mesh paramaters:")
e_size      = float(input("\tInput element size: "))
mesh_name   = str(input("\tInput mesh name: "))

# Output all parameters
print("Parameters")
print(f"\tMajor radius:\t{r_major}")
print(f"\tMinor radius:\t{r_minor}")
print(f"\Element size:\t{e_size}")
print(f"\Mesh name:\t{mesh_name}")

# Setup gmsh
gmsh.initialize()
gmsh.logger.start()
gmsh.option.set_number("Mesh.Algorithm", 6)
gmsh.option.set_number("Mesh.Algorithm3D", 1)
gmsh.option.set_number("Mesh.RecombinationAlgorithm", 1)
gmsh.option.set_number("Mesh.SubdivisionAlgorithm", 2)
gmsh.option.set_number("Mesh.ElementOrder", 2)
gmsh.option.set_number("Mesh.MshFileVersion", 2.0)
gmsh.option.set_number("Mesh.Binary", 1)
gmsh.model.add("tokamak")

# Generate points
p_top       = gmsh.model.geo.add_point(r_major, 0, r_minor, e_size)
p_center    = gmsh.model.geo.add_point(r_major, 0, 0, e_size)
p_bottom    = gmsh.model.geo.add_point(r_major, 0, -r_minor, e_size)
p_side      = gmsh.model.geo.add_point(r_major + r_minor, 0, 0, e_size)

# Generate curves
c_intop     = gmsh.model.geo.add_line(p_top, p_center)
c_inbottom  = gmsh.model.geo.add_line(p_center, p_bottom)
c_outbottom = gmsh.model.geo.add_circle_arc(p_bottom, p_center, p_side)
c_outtop    = gmsh.model.geo.add_circle_arc(p_side, p_center, p_top)
c_ewall     = [[1, c_intop], [1, c_inbottom], [1, c_outbottom], [1, c_outtop]]

# Copy cross section to west side as gmsh.model.geo only allows for revolutions less than pi
c_wwall     = gmsh.model.geo.copy(c_ewall)
gmsh.model.geo.rotate(c_wwall, 0, 0, 0, 0, 0, 1, math.pi)

# Revolve walls
s_wallne    = gmsh.model.geo.revolve(c_ewall, 0, 0, 0, 0, 0, 1, math.pi/2)
s_wallse    = gmsh.model.geo.revolve(c_ewall, 0, 0, 0, 0, 0, 1, -math.pi/2)
s_wallnw    = gmsh.model.geo.revolve(c_wwall, 0, 0, 0, 0, 0, 1, math.pi/2)
s_wallsw    = gmsh.model.geo.revolve(c_wwall, 0, 0, 0, 0, 0, 1, -math.pi/2)

# Extract surfaces
s_array = []
for dimTag in  s_wallne:
    if dimTag[0] == 2:
        s_array.append(dimTag[1])
for dimTag in  s_wallse:
    if dimTag[0] == 2:
        s_array.append(dimTag[1])
for dimTag in  s_wallnw:
    if dimTag[0] == 2:
        s_array.append(dimTag[1])
for dimTag in  s_wallsw:
    if dimTag[0] == 2:
        s_array.append(dimTag[1])

# Create tokamak volume
sl_tokamak  = gmsh.model.geo.add_surface_loop(s_array)
v_tokamak   = gmsh.model.geo.add_volume([sl_tokamak])

# Create physical groups
g_wall      = gmsh.model.geo.add_physical_group(2, s_array)
gmsh.model.set_physical_name(2, g_wall, "Wall")
g_tokamak   = gmsh.model.geo.add_physical_group(3, [v_tokamak])
gmsh.model.set_physical_name(2, g_wall, "Tokamak")

# Generate mesh
gmsh.model.geo.synchronize()
gmsh.model.mesh.generate()

# Write the file and visualize
gmsh.write(f"{mesh_name}.msh")
gmsh.fltk.run()
gmsh.finalize()