import c4d,sys

#sys.path.append('/Library/Python/2.6/site-packages/numpy-override')

import numpy as npy
from numpy import zeros, array, sin, cos, dot, linalg, pi, asarray, mean, shape, sqrt, flipud, std, concatenate, ones, arccos, arcsin, arctan,arctan2, size, abs, matrix, diag
import random
from copy import copy

ID_OD_CALIBRATOR = 1059348

class CalibrageCamera(object):

    def __init__(self,bmp, uv,xyz):
        self.bmp = bmp
        self.sizePicture = self.bmp.GetSize()

        #transformation de liste de c4d vector en ltables numpy
        nb_pts = len(xyz)
        self.xyz = npy.zeros((nb_pts, 3))
        self.uv = npy.zeros((nb_pts, 2))

        for i,(p3D,pt_uv) in enumerate(zip(xyz,uv)):
            self.xyz[i,0] = p3D.x
            self.xyz[i,1] = p3D.y
            self.xyz[i,2] = p3D.z

            self.uv[i,0] = pt_uv.x
            self.uv[i,1] = pt_uv.y

        self.camera = self.getCamera(self.xyz,self.uv)


    def getCamera(self,xyz,uv1):
        """renvoie une camera calibree Cinema4D"""
        self.estimatePose(xyz,uv1)
        camera = c4d.BaseObject(c4d.Ocamera)
        #camera[c4d.CAMERA_FOCUS] = #distance focale
        camera.SetMg(self.mg_cam)
        camera[c4d.CAMERAOBJECT_FOV_VERTICAL] = self.focale
        return camera

    def estimatePose(self,xyz,uv1):
        #attention je n'ai pas compris l'utilite de fixed ou pas (voir ligne 140 de posedialog.py de pic2map)
        #regarder sur la video de presentation a 4'20''
        """
        Read the list of Parameter of camera
        0. X Position
        1. Y Position
        2. Z Position
        3. Tilt
        4. heading
        5. swing
        6. focal
        Parameters 7 and 8 are the central point. It is fixed to the center of image for convenience with openGL
        parameter_bool is an array with 0 if the parameter is fixed, or 1 if the parameter is free
        """
        #pourl'instant je mets tout a 1 -> non fixed
        parameter_bool = zeros((9))
        parameter_list = []

        for i in range(7):
            parameter_bool[i] = 1

        # We fix anyway the central point. Future work can take it into account. It is therefore used here as parameter.
        #U0
        parameter_bool[7] = 0
        parameter_list.append(self.sizePicture[0]/2)
        #V0
        parameter_bool[8] = 0
        parameter_list.append(self.sizePicture[1]/2)



        resultInitialization, L, v = self.DLTMain(xyz,uv1)

        resultLS, Lproj, vect = self.LS(xyz,uv1,parameter_bool,parameter_list,resultInitialization)

        k = 0
        l = 0
        result = [0]*9
        # Length of resultLS is [9 - length of parameter_list]
        # We reconstruct the "result" vector which contains the output parameters
        for i in range(9):
            if parameter_bool[i]:
                result[i] = resultLS[k]
                k +=1
            else:
                result[i]=parameter_list[l]
                l +=1
        indice = 0

        # Set result in the dialog box
        for line in range(9):
            value = result[indice]
            if indice == 0:
                value *= -1
            if indice > 2 and indice < 6:
                value *= 180/pi
            if indice == 7:
                value-=self.sizePicture[0]/2.0
            if indice == 8:
                value-=self.sizePicture[1]/2.0
            #line.setText(str(round(value,3)))
            #print (indice,'->',value)
            indice +=1


        #Set the variable for next computation and for openGL pose
        self.parameter_bool = parameter_bool
        self.parameter_list = parameter_list
        self.done = True
        self.result = result
        self.LProj = Lproj
        self.lookat = vect
        #print (vect)


        self.pos = result[0:3]
        #print (self.pos)

        # The focal, here calculate in pixel, has to be translated in term of vertical field of view for openGL
        self.focale = (2*arctan(float(self.sizePicture[1]/2.0)/result[6]))

        #JE N'AI PAS COMPRIS L'UTILITE DU ROLL, j'ai teste avec une rotation sur l'axe x mais c'est bizarre (angle de 45)
        # a teste plus en detail en faisant tourner la camera de base sur l'axe z
        self.roll = arcsin(-sin(result[3])*sin(result[5]))
        #print (self.roll)

        #test matrice pour camera
        pos = c4d.Vector(result[0],result[1],result[2])
        direction = c4d.Vector(vect[0],vect[1],vect[2])-pos
        hpb = c4d.utils.VectorToHPB(direction)
        self.mg_cam =c4d.utils.HPBToMatrix(hpb)

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #A VERIFIER NE FONCTIONNE PAS !!!!!!!!!!!!!!!!!!!!!!
        m_rot = c4d.utils.MatrixRotZ(self.roll)
        self.mg_cam *= m_rot
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        self.mg_cam.off = pos


        #self.v1 = lookat
        #self.v3 =



    def LS(self,abscissa,observations,PARAM,x_fix,x_ini):
        # The initial parameters are the ones from DLT but where the radio button is set as free
        x = []
        for i in range(9):
            if PARAM[i]:
                x.append(x_ini[i])
        x = array(x)
        # 2D coordinates are understood as observations
        observations = npy.array(observations)
        # 3D coordinates are understood as the abscissas
        abscissa = npy.array(abscissa)
        npoints = npy.size(observations[:,1])

        l_x = int(sum(PARAM));
        sigmaobservationservation = 1
        Kl =  npy.zeros(shape=(2*npoints,2*npoints))

        # A error of "sigmaobservationservation" pixels is a priori set
        for i in range (npoints):
            Kl[2*i-1,2*i-1]=sigmaobservationservation**2
            Kl[2*i,2*i]=sigmaobservationservation**2

        # The P matrix is a weight matrix, useless if equal to identity (but can be used in some special cases)
        P=npy.linalg.pinv(Kl);
        # A is the Jacobian matrix
        A = npy.zeros(shape=(2*npoints,l_x))
        # H is the hessian matrix
        H = npy.zeros(shape=(l_x,l_x))
        # b is a transition matrix
        b = npy.zeros(shape=(l_x))
        # v contains the residual errors between observations and predictions
        v = npy.zeros(shape=(2*npoints))
        # v_test contain the residual errors between observations and predictions after an update of H
        v_test = npy.zeros(shape=(2*npoints))
        # x_test is the updated parameters after an update of H
        x_test = npy.zeros(shape=(l_x))
        # dx is the update vector of x and x_test
        dx = npy.array([0.]*l_x)


        it=-1;
        maxit=1000;
        # At least one iteration, dx > inc
        dx[0]=1
        # Lambda is the weightage parameter in Levenberg-marquart between the gradient and the gauss-newton parts.
        Lambda = 0.01
        # increment used for Jacobian and for convergence criterium
        inc = 0.001
        while (max(abs(dx))> inc) & (it<maxit):
            #new iteration, parameters updates are greater than the convergence criterium
            it=it+1;
            # For each observations, we compute the derivative with respect to each parameter
            # We form therefore the Jacobian matrix
            for i in range(npoints):
                #ubul and vbul are the prediction with current parameters
                ubul, vbul = self.dircal(x,abscissa[i,:],x_fix,PARAM)
                # The difference between the observation and prediction is used for parameters update
                v[2*i-1]=observations[i,0]-ubul
                v[2*i]=observations[i,1]-vbul
                for j in range(l_x):
                    x_temp = copy(x);
                    x_temp[j] = x[j]+inc
                    u2, v2 = self.dircal(x_temp,abscissa[i,:],x_fix,PARAM)
                    A[2*i-1,j]= (u2-ubul)/inc
                    A[2*i,j]= (v2-vbul)/inc
            # The sum of the square of residual (S0) must be as little as possible.
            # That's why we speak of "least square"... tadadam !
            S0 = sum(v**2);
            H = npy.dot(npy.dot(npy.matrix.transpose(A),P),A);
            b = npy.dot(npy.dot(npy.matrix.transpose(A),P),v);
            try:
                dx = npy.dot(npy.linalg.pinv(H+Lambda*npy.diag(npy.diag(H))),b);
                x_test = x+dx;
            except:
                # The matrix is not always reversal.
                # In this case, we don't accept the update and go for another iteration
                S2 = S0
            else:
                for i in range(npoints):
                    # We check that the update has brought some good stuff in the pocket
                    # In other words, we check that the sum of square of less than before (better least square!)
                    utest, vtest = self.dircal(x_test,abscissa[i,:],x_fix,PARAM);
                    v_test[2*i-1]=observations[i,0]-utest;
                    v_test[2*i]=observations[i,1]-vtest;
                    S2 = sum(v_test**2);
            # Check if sum of square is less
            if S2<S0:
                Lambda = Lambda/10
                x = x + dx
            else:
                Lambda = Lambda*10

        # Covariance matrix of parameters
        self.Qxx = sqrt(diag(linalg.inv(dot(dot(matrix.transpose(A),P),A))))

        p = zeros(shape=(len(PARAM)))
        m = 0
        n = 0
        for k in range(len(PARAM)):
            if PARAM[k]:
                p[k] = x[m]
                m = m+1
            else:
                p[k] = x_fix[n]
                n = n+1
        L1p = self.CoeftoMatrixProjection(p)

        x0 = p[0];
        y0 = p[1];
        z0 = p[2];
        tilt = p[3];
        azimuth = p[4];
        swing = p[5];
        focal = p[6];
        u0 = p[7];
        v0 = p[8];

        R = zeros((3,3))
        R[0,0] = -cos(azimuth)*cos(swing)-sin(azimuth)*cos(tilt)*sin(swing)
        R[0,1] =  sin(azimuth)*cos(swing)-cos(azimuth)*cos(tilt)*sin(swing)
        R[0,2] = -sin(tilt)*sin(swing)
        R[1,0] =  cos(azimuth)*sin(swing)-sin(azimuth)*cos(tilt)*cos(swing)
        R[1,1] = -sin(azimuth)*sin(swing)-cos(azimuth)*cos(tilt)*cos(swing)
        R[1,2] = -sin(tilt)*cos(swing)
        R[2,0] = -sin(azimuth)*sin(tilt)
        R[2,1] = -cos(azimuth)*sin(tilt)
        R[2,2] =  cos(tilt)

        # Get "look at" vector for openGL pose
        not_awesome_vector = array([0,0,-focal])
        almost_awesome_vector = dot(linalg.inv(R),not_awesome_vector.T)
        awesome_vector = array(almost_awesome_vector)+array([x0,y0,z0])

        return x, L1p, awesome_vector

    def CoeftoMatrixProjection(self,x):
        L1p = zeros((4,4))
        L1_line = zeros(12)
        x0 = x[0]
        y0 = x[1]
        z0 = x[2]
        tilt = x[3]
        azimuth = x[4]
        swing = x[5]
        focal = x[6]
        u0 = x[7]
        v0 = x[8]
        R = zeros((3,3))
        R[0,0] = -cos(azimuth)*cos(swing)-sin(azimuth)*cos(tilt)*sin(swing)
        R[0,1] =  sin(azimuth)*cos(swing)-cos(azimuth)*cos(tilt)*sin(swing)
        R[0,2] = -sin(tilt)*sin(swing)
        R[1,0] =  cos(azimuth)*sin(swing)-sin(azimuth)*cos(tilt)*cos(swing)
        R[1,1] = -sin(azimuth)*sin(swing)-cos(azimuth)*cos(tilt)*cos(swing)
        R[1,2] = -sin(tilt)*cos(swing)
        R[2,0] = -sin(azimuth)*sin(tilt)
        R[2,1] = -cos(azimuth)*sin(tilt)
        R[2,2] =  cos(tilt)
        D = -(x0*R[2,0]+y0*R[2,1]+z0*R[2,2])
        L1_line[0] = (u0*R[2,0]-focal*R[0,0])/D
        L1_line[1] = (u0*R[2,1]-focal*R[0,1])/D
        L1_line[2] = (u0*R[2,2]-focal*R[0,2])/D
        L1_line[3] = ((focal*R[0,0]-u0*R[2,0])*x0+(focal*R[0,1]-u0*R[2,1])*y0+(focal*R[0,2]-u0*R[2,2])*z0)/D
        L1_line[4] = (v0*R[2,0]-focal*R[1,0])/D
        L1_line[5] = (v0*R[2,1]-focal*R[1,1])/D
        L1_line[6] = (v0*R[2,2]-focal*R[1,2])/D
        L1_line[7] = ((focal*R[1,0]-v0*R[2,0])*x0+(focal*R[1,1]-v0*R[2,1])*y0+(focal*R[1,2]-v0*R[2,2])*z0)/D
        L1_line[8] = R[2,0]/D
        L1_line[9] = R[2,1]/D
        L1_line[10] = R[2,2]/D
        L1_line[11] = 1
        L1p =  L1_line.reshape(3,4)
        return L1p

    def dircal(self,x_unkown,abscissa,x_fix,PARAM):
        p = npy.zeros(shape=(len(PARAM)))
        m = 0
        n = 0
        for k in range(len(PARAM)):
            if PARAM[k]:
                p[k] = x_unkown[m]
                m = m+1
            else:
                p[k] = x_fix[n]
                n = n+1
        x1 = abscissa[0];
        y1 = abscissa[1];
        z1 = abscissa[2];
        x0 = p[0];
        y0 = p[1];
        z0 = p[2];
        tilt = p[3];
        azimuth = p[4];
        swing = p[5];
        focal = p[6];
        u0 = p[7];
        v0 = p[8];
        R = zeros((3,3))
        R[0,0] = -cos(azimuth)*cos(swing)-sin(azimuth)*cos(tilt)*sin(swing)
        R[0,1] =  sin(azimuth)*cos(swing)-cos(azimuth)*cos(tilt)*sin(swing)
        R[0,2] = -sin(tilt)*sin(swing)
        R[1,0] =  cos(azimuth)*sin(swing)-sin(azimuth)*cos(tilt)*cos(swing)
        R[1,1] = -sin(azimuth)*sin(swing)-cos(azimuth)*cos(tilt)*cos(swing)
        R[1,2] = -sin(tilt)*cos(swing)
        R[2,0] = -sin(azimuth)*sin(tilt)
        R[2,1] = -cos(azimuth)*sin(tilt)
        R[2,2] =  cos(tilt)

        ures = -focal*(R[0,0]*(x1-x0)+R[0,1]*(y1-y0)+R[0,2]*(z1-z0))/\
            (R[2,0]*(x1-x0)+R[2,1]*(y1-y0)+R[2,2]*(z1-z0))+u0;
        vres = -focal*(R[1,0]*(x1-x0)+R[1,1]*(y1-y0)+R[1,2]*(z1-z0))/\
            (R[2,0]*(x1-x0)+R[2,1]*(y1-y0)+R[2,2]*(z1-z0))+v0;

        return ures,vres

    def Normalization(self, nd,x):
        # written by Marcos Duarte - duartexyz@gmail.com
        """Normalization of coordinates (centroid to the origin and mean distance of sqrt(2 or 3)).
        Inputs:
         nd: number of dimensions (2 for 2D; 3 for 3D)
         x: the data to be normalized (directions at different columns and points at rows)
        Outputs:
         Tr: the transformation matrix (translation plus scaling)
         x: the transformed data
        """
        x = npy.asarray(x)
        m = npy.mean(x,0)
        if nd==2:
            Tr = npy.array([[npy.std(x[:,0]), 0, m[0]], [0, npy.std(x[:,1]), m[1]], [0, 0, 1]])
        else:
            Tr = npy.array([[npy.std(x[:,0]), 0, 0, m[0]], [0, npy.std(x[:,1]), 0, m[1]], [0, 0, npy.std(x[:,2]), m[2]], [0, 0, 0, 1]])

        Tr = npy.linalg.inv(Tr)

        x = npy.dot( Tr, npy.concatenate( (x.T, npy.ones((1,x.shape[0]))) ) )
        x = x[0:nd,:].T
        return Tr, x

    def DLTcalibration(self,xyz, uv):
        # written by Marcos Duarte - duartexyz@gmail.com
        """
        Methods for camera calibration and point reconstruction based on DLT.

        DLT is typically used in two steps:
        1. Camera calibration. Function: L, err = DLTcalib(nd, xyz, uv).
        2. Object (point) reconstruction. Function: xyz = DLTrecon(nd, nc, Ls, uvs)

        The camera calibration step consists in digitizing points with known coordinates
         in the real space and find the camera parameters.
        At least 4 points are necessary for the calibration of a plane (2D DLT) and at
         least 6 points for the calibration of a volume (3D DLT). For the 2D DLT, at least
         one view of the object (points) must be entered. For the 3D DLT, at least 2
         different views of the object (points) must be entered.
        These coordinates (from the object and image(s)) are inputed to the DLTcalib
         algorithm which estimates the camera parameters (8 for 2D DLT and 11 for 3D DLT).
        Usually it is used more points than the minimum necessary and the overdetermined
         linear system is solved by a least squares minimization algorithm. Here this
         problem is solved using singular value decomposition (SVD).
        With these camera parameters and with the camera(s) at the same position of the
         calibration step, we now can reconstruct the real position of any point inside
         the calibrated space (area for 2D DLT and volume for the 3D DLT) from the point
         position(s) viewed by the same fixed camera(s).
        This code can perform 2D or 3D DLT with any number of views (cameras).
        For 3D DLT, at least two views (cameras) are necessary.
        """
        """
        Camera calibration by DLT using known object points and their image points.

        This code performs 2D or 3D DLT camera calibration with any number of views (cameras).
        For 3D DLT, at least two views (cameras) are necessary.
        Inputs:
         nd is the number of dimensions of the object space: 3 for 3D DLT and 2 for 2D DLT.
         xyz are the coordinates in the object 3D or 2D space of the calibration points.
         uv are the coordinates in the image 2D space of these calibration points.
         The coordinates (x,y,z and u,v) are given as columns and the different points as rows.
         For the 2D DLT (object planar space), only the first 2 columns (x and y) are used.
         There must be at least 6 calibration points for the 3D DLT and 4 for the 2D DLT.
        Outputs:
         L: array of the 8 or 11 parameters of the calibration matrix.
         err: error of the DLT (mean residual of the DLT transformation in units
          of camera coordinates).
        """

        # Convert all variables to numpy array:
        xyz = npy.asarray(xyz)
        uv = npy.asarray(uv)
        # Number of points:
        npoints = xyz.shape[0]
        # Check the parameters:

        # Normalize the data to improve the DLT quality (DLT is dependent on the
        #  system of coordinates).
        # This is relevant when there is a considerable perspective distortion.
        # Normalization: mean position at origin and mean distance equals to 1
        #  at each direction.
        Txyz, xyzn = self.Normalization(3,xyz)
        Tuv, uvn = self.Normalization(2, uv)
        # Formulating the problem as a set of homogeneous linear equations, M*p=0:
        A = []
        for i in range(npoints):
            x,y,z = xyzn[i,0], xyzn[i,1], xyzn[i,2]
            u,v = uvn[i,0], uvn[i,1]
            A.append( [x, y, z, 1, 0, 0, 0, 0, -u*x, -u*y, -u*z, -u] )
            A.append( [0, 0, 0, 0, x, y, z, 1, -v*x, -v*y, -v*z, -v] )

        # Convert A to array:
        A = npy.asarray(A)
        # Find the 11 (or 8 for 2D DLT) parameters:

        U, S, Vh = npy.linalg.svd(A)
        # The parameters are in the last line of Vh and normalize them:
        L = Vh[-1,:] / Vh[-1,-1]
        # Camera projection matrix:
        H = L.reshape(3,4)

        # Denormalization:
        H = npy.dot( npy.dot( npy.linalg.pinv(Tuv), H ), Txyz );
        H = H / H[-1,-1]
        #print(H)
        #L = H.flatten(0)
        L = H.flatten()
        # Mean error of the DLT (mean residual of the DLT transformation in
        #  units of camera coordinates):
        uv2 = npy.dot( H, npy.concatenate( (xyz.T, npy.ones((1,xyz.shape[0]))) ) )
        uv2 = uv2/uv2[2,:]
        # Mean distance:
        err = npy.sqrt( npy.mean(sum( (uv2[0:2,:].T - uv)**2,1 )) )
        return L, err

    def DLTMain(self,xyz,uv1):
            L1, err1 = self.DLTcalibration(xyz, uv1)
            L1p = npy.array([[L1[0],L1[1],L1[2], L1[3]],[L1[4], L1[5], L1[6], L1[7]],[L1[8], L1[9], L1[10], L1[11]]])

            #Reconstruction of parameters
            D2=1/(L1[8]**2+L1[9]**2+L1[10]**2);
            D = npy.sqrt(D2);
            u0 = D2*(L1[0]*L1[8]+L1[1]*L1[9]+L1[2]*L1[10]);
            v0 = D2*(L1[4]*L1[8]+L1[5]*L1[9]+L1[6]*L1[10]);
            x0y0z0 = npy.dot(npy.linalg.pinv(L1p[0:3,0:3]),[[-L1[3]],[-L1[7]],[-1]]);
            du2 = D2*((u0*L1[8]-L1[0])**2+(u0*L1[9]-L1[1])**2+(u0*L1[10]-L1[2])**2);
            dv2 = D2*((v0*L1[8]-L1[4])**2+(v0*L1[9]-L1[5])**2+(v0*L1[10]-L1[6])**2);
            du = npy.sqrt(du2);
            dv = npy.sqrt(dv2);
            focal = (du+dv)/2

            R_mat = npy.array([[(u0*L1[8]-L1[0])/du,(u0*L1[9]-L1[1])/du,(u0*L1[10]-L1[2])/du],\
                    [(v0*L1[8]-L1[4])/dv,(v0*L1[9]-L1[5])/dv,(v0*L1[10]-L1[6])/dv],\
                    [L1[8],L1[9],L1[10]]]);

            if npy.linalg.det(R_mat) < 0:
                R_mat = -R_mat;
            R = D * npy.array(R_mat);
            U,s,V = npy.linalg.svd(R,full_matrices=True,compute_uv=True)
            R = npy.dot(U,V)


            tilt = npy.arccos(R[2,2])
            swing = npy.arctan2(-R[0,2],-R[1,2])
            azimuth = npy.arctan2(-R[2,0],-R[2,1])
            not_awesome_vector = npy.array([-u0+self.sizePicture[0]/2,-v0+self.sizePicture[1]/2,-focal])

            almost_awesome_vector = npy.dot(npy.linalg.inv(R),not_awesome_vector)
            awesome_vector = npy.array(almost_awesome_vector)+npy.array([x0y0z0[0,0],x0y0z0[1,0],x0y0z0[2,0]])
            #print (awesome_vector)

            #adaptation OD
            self.pos_camera = c4d.Vector(x0y0z0[0,0],x0y0z0[1,0],x0y0z0[2,0])
            # The focal, here calculate in pixel, has to be translated in term of vertical field of view for openGL
            self.focal = (2*npy.arctan(float(self.sizePicture[1]/2.0)/focal))*180/npy.pi
            #print ('position : ', self.pos_camera)
            #print ('focale  :', self.focal)
            #print (tilt,azimuth,swing)
            #print ('tilt    : ',c4d.utils.Deg(tilt))
            #print ('azimuth : ', c4d.utils.Deg(azimuth))
            #print ('swing   : ', c4d.utils.Deg(swing))
            return [x0y0z0[0,0],x0y0z0[1,0],x0y0z0[2,0],tilt,azimuth,swing,focal,u0,v0], L1p ,awesome_vector


def main():
    if op and op[ID_OD_CALIBRATOR]:
        bc = op[ID_OD_CALIBRATOR]
        fn_img = bc[0]
        bmp = c4d.bitmaps.BaseBitmap()
        if bmp.InitWith(fn_img):
            pts_uv = [v for i,v in bc[1]]
            print(bmp.GetSize())
            print(pts_uv)
            pts_3D = [o.GetMg().off for o in op.GetChildren()]
            print(pts_3D)

            if len(pts_uv) != len(pts_3D):
                print("pas le même nombre de points")
                return
            cal_cam = CalibrageCamera(bmp,pts_uv,pts_3D)
            cam = cal_cam.camera
            doc.InsertObject(cam)
            c4d.EventAdd()


if __name__ == "__main__":
    main()