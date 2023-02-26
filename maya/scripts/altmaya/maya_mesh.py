import time

import numpy

import maya.cmds as cmds
import maya.api.OpenMaya as om

import AltMaya as altmaya


query_space = om.MSpace.kObject


class Vertex:
    
    
    def __init__(self, parent, m_mesh, index):
        self.parent = parent
        self.m_mesh = m_mesh
        self.index = index
        
        self.p = self.m_mesh.getPoint(self.index, query_space)
        self.n = self.m_mesh.getVertexNormal(self.index, False, query_space).normalize()
           
        self.starting_p = om.MPoint(self.p)
        self.starting_n = om.MVector(self.n)
        self.delta_p = self.read_delta()
        
    def update(self):
        self.p = self.m_mesh.getPoint(self.index, query_space)
        self.n = self.m_mesh.getVertexNormal(self.index, False, query_space).normalize() # False turns of angle-weighting and is faster
        self.delta_p = self.read_delta()        
        
    def as_array(self):
        return numpy.array([
            [self.p[0]],
            [self.p[1]], 
            [self.p[2]]
        ])

    def as_array_4(self):
        return numpy.array([
            [self.p[0]],
            [self.p[1]], 
            [self.p[2]],
            1.0
        ])        
        
    def reset(self):
        self.m_mesh.setPoint(self.index, self.starting_p, query_space)
    
    def set_by_maya_point(self, point):
        self.p = om.MPoint(point)
        self.m_mesh.setPoint(self.index, self.p, query_space)
        
    def set_by_xyz(self, x, y, z):
        self.p = om.MPoint(x, y, z)
        self.m_mesh.setPoint(self.index, self.p, query_space)
        
    def set_by_array(self, array):
        x = array[0]
        y = array[1]
        z = array[2]
        self.set_by_xyz(x, y, z)
        
    def set_by_xyz_delta(self, x, y, z):
        self.set_by_xyz(
            x + self.starting_p[0],
            y + self.starting_p[1],
            z + self.starting_p[2]
        )
        
    def read_delta(self):
        return om.MPoint(
            self.starting_p[0] - self.p[0],
            self.starting_p[1] - self.p[1], 
            self.starting_p[2] - self.p[2])
        
    def __str__(self):
        return "Vertex[%d,(%2.2f %2.2f %2.2f)]" % (self.index, self.p[0], self.p[1], self.p[2])

    def as_key(self):
        return "%s.vtx[%d]" % (self.parent.name, self.index) 

    def select(self):
        altmaya.Selection.set([self.as_key()])


class Triangle:
    
    def __init__(self, parent, m_mesh, index, v1, v2, v3):
        self.parent = parent
        self.m_mesh = m_mesh
        self.index = index
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.n = self.m_mesh.getPolygonNormal(self.index, query_space).normalize()
        
        v1 = self.v1.as_array()
        v2 = self.v2.as_array()
        v3 = self.v3.as_array()
        v2v1 = v2 - v1
        v3v1 = v3 - v1
        self.original_centroid = (v1 + v2 + v3) / 3
        self.original_edge_matrix = numpy.matrix(numpy.hstack([v2v1, v3v1]))
        
        q, r = numpy.linalg.qr(self.original_edge_matrix)
        try:
            self.original_r1qt = r.I * q.T
        except numpy.linalg.linalg.LinAlgError as e:
            print(
                "Failed to init R1QT for %s.f[%d] faking it as zeros (error is %s)" % (
                    self.parent.name, self.index, str(e)
                )
            )
            self.original_r1qt = numpy.matrix([[0,0,0], [0,0,0]])
        
        cp = numpy.cross(v2v1.T, v3v1.T)  # TODO - maybe should use face normal here instead?
        v4 = cp / numpy.linalg.norm(cp)
        self.original_simplex = numpy.matrix(numpy.hstack([v2v1, v3v1, v4.T]))

        self.centroid = self.original_centroid
        self.edge_matrix = self.original_edge_matrix
        self.r1qt = self.original_r1qt
        self.simplex = self.original_simplex
        
    def update(self, update_vertices=False):
        if update_vertices:
            self.v1.update()
            self.v2.update()
            self.v3.update()
        v1 = self.v1.as_array()
        v2 = self.v2.as_array()
        v3 = self.v3.as_array()
        v2v1 = v2 - v1
        v3v1 = v3 - v1
        self.centroid = (v1 + v2 + v3) / 3
        self.edge_matrix = numpy.matrix(numpy.hstack([v2v1, v3v1]))

        q, r = numpy.linalg.qr(self.edge_matrix)
        try:
            self.r1qt = r.I * q.T
        except numpy.linalg.linalg.LinAlgError as e:
            print(
                "Failed to update R1QT for %s.f[%d], faking it as zeros (error is %s)" % (
                    self.parent.name, self.parent.triangles.index(self), str(e)
                )
            )
            self.r1qt = numpy.matrix([[0,0,0], [0,0,0]])

        cp = numpy.cross(v2v1.T, v3v1.T)
        v4 = cp / numpy.linalg.norm(cp)
        # TODO - test getting maya normal here?!"
        self.simplex = numpy.matrix(numpy.hstack([v2v1, v3v1, v4.T]))
        
    def as_key(self):
        index = self.parent.triangles.index(self)
        return "%s.f[%d]" % (self.parent.name, index)
        
    def select(self):
        altmaya.Selection.set([self.as_key()])


class Mesh:

    def __init__(self, name, verbose=False):
        self.name = name

        self.m_mesh = altmaya.API.get_mesh_function_set_from_name(self.name)

        self.face_to_edge = {}
        for f2e in cmds.polyInfo(self.name, faceToEdge=True):
            f, es = f2e.split(":")
            face = int(f.split("FACE")[1].strip())
            edges = [int(v.strip()) for v in es.split(" ") if v.strip() != ""]
            self.face_to_edge[face] = edges
            
        self.edge_to_face = {}
        for e2f in cmds.polyInfo(self.name, edgeToFace=True):
            e, fs = e2f.split(":")
            edge = int(e.split("EDGE")[1].strip())
            faces = [int(v.strip()) for v in fs.split(" ") if v.strip() != ""]
            self.edge_to_face[edge] = faces 

        self.vertex_to_edge = {}
        for v2e in cmds.polyInfo(self.name, vertexToEdge=True):
            v, es = v2e.split(":")
            vertex = int(v.split("VERTEX")[1].strip())
            edges = [int(v.strip()) for v in es.split(" ") if v.strip() != ""]
            self.vertex_to_edge[vertex] = edges
            
        self.edge_to_vertex = {}
        for e2v in cmds.polyInfo(self.name, edgeToVertex=True):
            e, vs = e2v.split(":")
            edge = int(e.split("EDGE")[1].strip())
            vertices = [int(v.strip()) for v in vs.split(" ") if v.strip() != "" and v.strip() != "Hard"]
            self.edge_to_vertex[edge] = vertices 

        self.face_to_vertex = {}
        for f2v in cmds.polyInfo(self.name, faceToVertex=True):
            f, vs = f2v.split(":")
            face = int(f.split("FACE")[1].strip())
            vertices = [int(v.strip()) for v in vs.split(" ") if v.strip() != "" and v.strip() != "Hard"]
            self.face_to_vertex[face] = vertices 

        self.face_to_face = {}
        for curr_face in self.face_to_edge.keys():
            adj = []
            for e in self.face_to_edge[curr_face]:
                adj += [f for f in self.edge_to_face[e] if f != curr_face]
            self.face_to_face[curr_face] = adj

        self.edge_to_edge = {}
        for curr_edge in self.edge_to_vertex.keys():
            vertices = self.edge_to_vertex[curr_edge]
            adj = []
            for v in vertices:
                adj += [e for e in self.vertex_to_edge[v] if e != curr_edge]
            self.edge_to_edge[curr_edge] = adj

        if verbose: s = time.time()
        self.vertices = [
            Vertex(self, self.m_mesh, i)
            for i in range(self.m_mesh.numVertices)
        ]
        if verbose: e = time.time()
        if verbose: print("Verts init took %2.2fs" % (e-s))
        
        if verbose: s = time.time()
        self.triangles = []
        for i in range(self.m_mesh.numPolygons):
            inds = self.m_mesh.getPolygonVertices(i)
            if len(inds) != 3:
                raise ValueError("Can only process triangle meshes for now, sorry (face %d has %d verts)" % (i, len(inds)))
            t = Triangle(
                self,
                self.m_mesh,
                i,
                self.vertices[inds[0]],
                self.vertices[inds[1]],
                self.vertices[inds[2]]
            )    
            self.triangles.append(t)
        if verbose: e = time.time()
        if verbose: print("Triangles init took %2.2fs" % (e-s))  
        
    def as_copy(self, verbose=False):
        return Mesh(self.name, existing=self, verbose=verbose)      

    def get_index_of_face_nearest_point(self, x, y, z):
        query = om.MPoint(x, y, z)
        _, ix = self.m_mesh.getClosestPoint(query, query_space)
        return ix

    def get_index_of_vertex_nearest_point(self, x, y, z):
        q = om.MPoint(x, y, z)
        ix = self.get_index_of_face_nearest_point(x, y, z)
        t = self.triangles[ix]
        d_v1 = q.distanceTo(t.v1.p)
        d_v2 = q.distanceTo(t.v2.p)
        d_v3 = q.distanceTo(t.v3.p)
        if d_v1 <= d_v2 and d_v1 <= d_v3:
            return t.v1.index
        elif d_v2 <= d_v1 and d_v2 <= d_v3:
            return t.v2.index
        elif d_v3 <= d_v1 and d_v3 <= d_v2:
            return t.v3.index
        else:
            raise ValueError("Couldn't decide the closest point, this shouldn't happen?")

    def get_cooordinate_of_nearest_point(self, x, y, z):
        query = om.MPoint(x, y, z)
        coordinate, _ = self.m_mesh.getClosestPoint(query, query_space)
        return coordinate
		
    def get_coordinate_normal_and_face_of_nearest_point(self, x, y, z):
		query = om.MPoint(x, y, z)
		coord, normal, index = self.m_mesh.getClosestPointAndNormal(query, query_space)
		return coord, normal, index
        
    def reset(self, verbose=False):
        s = time.time()
        ps = []
        for v in self.vertices:
            ps.append(v.starting_p)
        e = time.time()
        if verbose: print("gather reset positions took %2.2fs" % (e-s))

        s = time.time()
        self.m_mesh.setPoints(ps, query_space)
        e = time.time()
        if verbose: print("resetting vertices took %2.2fs" % (e-s))
        
    def update(self, triangles=True, verts=True, verbose=False):
        if verts:
            s = time.time()        
            for v in self.vertices: v.update()
            e = time.time()
            if verbose: print("updating verts took %2.2fs" % (e-s))

        if triangles:
            s = time.time()
            for t in self.triangles: t.update()
            e = time.time()
            if verbose: print("updating tris took %2.2fs" % (e-s))
	
    def select_vertices_given_indices(self, inds):
		altmaya.Selection.set([
			"%s.vtx[%d]" % (self.name, i)
			for i in inds
		])
		
    def select_edges_given_indices(self, inds):
		altmaya.Selection.set([
			"%s.e[%d]" % (self.name, i)
			for i in inds
		])
		
    def select_faces_given_indices(self, inds):
		altmaya.Selection.set([
			"%s.f[%d]" % (self.name, i)
			for i in inds
		])
		
    def set_vertex_positions_by_matrix(self, matrix, verbose=False):
        s = time.time()
        ps = []
        for row in matrix:
            p = om.MPoint(row[0], row[1], row[2])
            ps.append(p)
        e = time.time()
        if verbose: print("gather desired positions took %2.2fs" % (e-s))

        s = time.time()
        self.m_mesh.setPoints(ps, query_space)
        e = time.time()
        if verbose: print("setting vertices took %2.2fs" % (e-s))

    def set_vertex_positions_by_mpoints_list(self, list_mpoint, verbose=False):
        s = time.time()
        self.m_mesh.setPoints(list_mpoint, query_space)
        e = time.time()
        if verbose: print("setting vertices took %2.2fs" % (e-s))
   
    def set_vertex_positions_by_2d_list(self, list_2d, verbose=False):
        s = time.time()
        ps = []
        for row in list_2d:
            p = om.MPoint(row[0], row[1], row[2])
            ps.append(p)
        e = time.time()
        if verbose: print("gather desired positions took %2.2fs" % (e-s))

        self.set_vertex_positions_by_mpoints_list(ps, verbose=verbose)

    def deform_to_fit_other_mesh_with_same_topology(self, other, verbose=False):
        a = self.name
        b = other.name
       
        # Check vertex count matches
        n_a = len(self.vertices)
        n_b = len(other.vertices)
        if n_a != n_b:
            raise ValueError("Both %s and %s need to have the same number of verts (%s has %d, %s has %d)" % (a, b, a, n_a, b, n_b))
        
        # Check face count matches
        n_a = len(self.triangles)
        n_b = len(other.triangles)
        if n_a != n_b:
            raise ValueError("Both %s and %s need to have the same number of verts (%s has %d, %s has %d)" % (a, b, a, n_a, b, n_b))
        
        self.set_vertex_positions_by_mpoints_list([v.p for v in other.vertices], verbose=verbose)
            
    def organize_list_of_edges_into_loop_order(self, boundary_edges):
        boundary_edges_unvisited = [
            ix for ix in boundary_edges
        ]

        starting_edge = boundary_edges_unvisited.pop()  
        loop = [starting_edge]
        curr_edge = starting_edge 
        iters = 0

        while True:
            adj = self.edge_to_edge[curr_edge]
            adj_boundary = [ix for ix in adj if ix in boundary_edges]
            adj_boundary_allowed = [ix for ix in adj_boundary if ix in boundary_edges_unvisited]
            if len(adj_boundary_allowed) == 0:
                if starting_edge in adj_boundary:
                    return loop
                else:
                    raise ValueError(
                        "Loop not found, the last allowed edge (%d) is not adjacent to the first edge (%d)?" % 
                        (curr_edge, starting_edge)
                    )
            else:
                adj_boundary_first = adj_boundary_allowed[0]
                boundary_edges_unvisited.remove(adj_boundary_first)
                loop.append(adj_boundary_first)
                curr_edge = adj_boundary_first

            iters += 1
            if iters > 10000:
                raise ValueError("Exceed inner loop search limit of 10000 iters")

    def get_edges_of_holes_in_mesh(self):
        boundary_edges = [
            ix 
            for (ix, k) in enumerate(self.edge_to_face.keys())
            if len(self.edge_to_face[k]) == 1
        ]
            
        boundary_edges_unvisited = [
            ix for ix in boundary_edges
        ]

        def trace_loop():
            starting_edge = boundary_edges_unvisited.pop()  
            loop = [starting_edge]
            curr_edge = starting_edge 
            iters = 0
            while True:
                adj = self.edge_to_edge[curr_edge]
                adj_boundary = [ix for ix in adj if ix in boundary_edges]
                adj_boundary_allowed = [ix for ix in adj_boundary if ix in boundary_edges_unvisited]
                if len(adj_boundary_allowed) == 0:
                    if starting_edge in adj_boundary:
                        return loop
                    else:
                        raise ValueError(
                            "Loop not found, the last allowed edge (%d) is not adjacent to the first edge (%d)?" % 
                            (curr_edge, starting_edge)
                        )
                else:
                    adj_boundary_first = adj_boundary_allowed[0]
                    boundary_edges_unvisited.remove(adj_boundary_first)
                    loop.append(adj_boundary_first)
                    curr_edge = adj_boundary_first

                iters += 1
                if iters > 10000:
                    raise ValueError("Exceed inner loop search limit of 10000 iters")

        loops = []
        outer_iters = 0
        while len(boundary_edges_unvisited) > 0:
            loop = trace_loop()
            loops.append(loop)
            outer_iters += 1
            if outer_iters > 100:
                raise ValueError("Failed to terminate the outer loop search after 100 iters")
        return loops

    def get_vertex_mapping_to_other(self, other):
        m = {}
        for v in self.vertices:
            
            # Get nearest face on org mesh
            ix = other.get_index_of_face_nearest_point(v.p[0], v.p[1], v.p[2])
            
            # Get vertices of nearest face
            v_ixs = other.face_to_vertex[ix]
            
            # Find closest vertex
            nearest_dist = float('inf')
            nearest_ix = -1
            for ix in v_ixs:
                ov = other.vertices[ix]
                d = ov.p.distanceTo(v.p)
                if d < nearest_dist:
                    nearest_dist = d
                    nearest_ix = ix
            
            # save it to the map
            m[v.index] = nearest_ix

        return m