import sys
import os
import math
import numpy as np
import gmsh

gmsh.initialize(sys.argv)
gmsh.logger.start()
gmsh.option.set_number("Mesh.Algorithm", 6)
gmsh.option.set_number("Mesh.Algorithm3D", 1)
gmsh.option.set_number("Mesh.RecombinationAlgorithm", 1)
#gmsh.option.set_number("Mesh.RecombineAll", 1)
gmsh.option.set_number("Mesh.SubdivisionAlgorithm", 2)
gmsh.option.set_number("Mesh.ElementOrder", 2)
gmsh.option.set_number("Mesh.MshFileVersion", 2.0)
gmsh.option.set_number("Mesh.Binary", 1)
gmsh.model.add("tokamak")

# Input parameters
r_major     = float(input("Input major radius in meters: "))
r_minor     = float(input("Input minor radius in meters: "))
e_size      = float(input("Input element size: "))
mesh_name   = str(input("Input mesh name: "))

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

# Write the file
gmsh.model.geo.synchronize()
gmsh.model.mesh.generate()
gmsh.write(f"{mesh_name}.msh")

if '-nopopup' not in sys.argv:
    gmsh.fltk.run()

# Inspect the log
log = gmsh.logger.get()
print("Logger has recorded " + str(len(log)) + " lines")
gmsh.logger.stop()
gmsh.finalize()