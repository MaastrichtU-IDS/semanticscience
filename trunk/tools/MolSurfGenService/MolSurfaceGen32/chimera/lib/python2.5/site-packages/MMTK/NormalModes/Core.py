# Common aspects of normal mode calculations.
#
# Written by Konrad Hinsen
# last revision: 2007-8-7
#

_undocumented = 1

from MMTK import Units, ParticleProperties, Visualization
from Scientific import N
import copy

#
# Import LAPACK routines or equivalents
#
try:
    array_package = N.package
except AttributeError:
    array_package = "Numeric"

symeig = None
if array_package == "NumPy":
    # Use symeig (http://mdp-toolkit.sourceforge.net/symeig.html)
    # if it is installed and if NumPy is used (symeig works only
    # with NumPy). Symeig uses the LAPACK routine dsyevr, which
    # uses less memory than dsyevd. It is also said to be faster,
    # but in my tests on the Mac it turned out to be slightly slower.
    try:
        from symeig import symeig
    except ImportError:
        pass

dsyevd = None
dgesdd = None
try:
    if array_package == "Numeric":
        from lapack_lite import dsyevd, dgesdd, LapackError
    else:
        from numpy.linalg.lapack_lite import dsyevd, dgesdd, LapackError
except ImportError: pass
if dsyevd is None:
    try:
        # PyLAPACK
        from lapack_dsy import dsyevd, LapackError
    except ImportError: pass
if dgesdd is None:
    try:
        # PyLAPACK
        from lapack_dge import dgesdd
    except ImportError: pass
if dsyevd is None:
    from Scientific.LA import Heigenvectors
if dsyevd:
    n = 1
    array = N.zeros((n, n), N.Float)
    ev = N.zeros((n,), N.Float)
    work = N.zeros((1,), N.Float)
    int_types = [N.Int, N.Int8, N.Int16, N.Int32]
    try:
        int_types.append(N.Int64)
        int_types.append(N.Int128)
    except AttributeError:
        pass
    for int_type in int_types:
        iwork = N.zeros((1,), int_type)
        try:
            dsyevd('V', 'L', n, array, n, ev, work, -1, iwork, -1, 0)
            break
        except LapackError:
            pass
    del n, array, ev, work, iwork, int_types

del array_package

#
# Class for a single mode
#
class Mode(ParticleProperties.ParticleVector):

    def __init__(self, universe, n, mode):
        self.number = n
        ParticleProperties.ParticleVector.__init__(self, universe, mode)

    return_class = ParticleProperties.ParticleVector

    def effectiveMassAndForceConstant(self):
        m = self.massWeightedProjection(self)/self.projection(self)
        k = m*(2.*N.pi*self.frequency)**2
        return m, k

    def view(self, factor=1., subset=None):
        """Start an animation of the mode. The displacements can be
        scaled by a |factor| to make them better visible, and
        a |subset| of the total system can be specified as well.
        This function requires an external viewer, see module
        Module:MMTK.Visualization for details."""
        Visualization.viewMode(self, factor, subset)

#
# Class for a full set of normal modes
# This is an abstract base class, the real classes are
# EnergeticModes, VibrationalModes, and BrownianModes
#
class NormalModes:

    def __init__(self, universe, basis, delta, sparse, arrays):
        self.universe = universe
        self.basis = basis
        if sparse:
            if isinstance(basis, int):
                self.sparse = basis
                self.basis = None
            else:
                self.sparse = -1
        else:
            self.sparse = None
        self.delta = delta
        self._internal_arrays = arrays

    def cleanup(self):
        del self.basis
        if self.sparse is not None:
            del self.fc

    def __len__(self):
        return self.nmodes

    def __getslice__(self, first, last):
        last = min(last, self.nmodes)
        return [self[i] for i in range(first, last)]

    def reduceToRange(self, first, last):
        """Discards all modes except for those whose numbers are between
        |first| (inclusive) and |last| (exclusive). This is done to
        reduce memory requirements, especially before saving the modes
        to a file."""
        junk1 = list(self.sort_index[:first])
        junk2 = list(self.sort_index[last:])
        junk1.sort()
        junk2.sort()
        if junk1 == range(0, first) and \
           junk2 == range(last, len(self.sort_index)):
            # This is the most frequent case. It can be handled
            # without copying the mode array.
            for array in self._internal_arrays:
                setattr(self, array, getattr(self, array)[first:last])
            self.sort_index = self.sort_index[first:last]-first
        else:
            keep = self.sort_index[first:last]
            for array in self._internal_arrays:
                setattr(self, array, N.take(getattr(self, array), keep))
            self.sort_index = N.arange(0, last-first)
        self.nmodes = last-first

    def _forceConstantMatrix(self):
        if self.basis is not None:
            self._setupBasis()
            if self.delta is not None:
                self.nmodes = len(self.basis)
                self.array = N.zeros((self.nmodes, self.nmodes), N.Float)
                conf = copy.copy(self.universe.configuration())
                conf_array = conf.array
                self.natoms = len(conf_array)
                small_change = 0
                for i in range(self.nmodes):
                    d = self.delta*N.reshape(self.basis[i],
                                             (self.natoms, 3))/self.weights
                    conf_array[:] = conf_array+d
                    self.universe.setConfiguration(conf)
                    energy, gradients1 = self.universe.energyAndGradients(
                                                     None, None, small_change)
                    small_change = 1
                    conf_array[:] = conf_array-2.*d
                    self.universe.setConfiguration(conf)
                    energy, gradients2 = self.universe.energyAndGradients(
                                                     None, None, small_change)
                    conf_array[:] = conf_array+d
                    v = (gradients1.array-gradients2.array) / \
                        (2.*self.delta*self.weights)
                    self.array[i] = N.dot(self.basis, N.ravel(v))
                self.universe.setConfiguration(conf)
                self.array = 0.5*(self.array+N.transpose(self.array))
                return
            elif self.sparse is not None:
                from MMTK_forcefield import SparseForceConstants
                nmodes, natoms = self.basis.shape
                natoms = natoms/3
                self.nmodes = nmodes
                self.natoms = natoms
                fc = SparseForceConstants(natoms, 5*natoms)
                eval = self.universe.energyEvaluator()
                energy, g, fc = eval(0, fc, 0)
                self.array = N.zeros((nmodes, nmodes), N.Float)
                for i in range(nmodes):
                    v = N.reshape(self.basis[i], (natoms, 3))/self.weights
                    v = fc.multiplyVector(v)
                    v = v/self.weights
                    v.shape = (3*natoms,)
                    self.array[i, :] = N.dot(self.basis, v)
                self.sparse = None
                return
        if self.sparse is None:
            energy, force_constants = self.universe.energyAndForceConstants()
            self.array = force_constants.array
            self.natoms = self.array.shape[0]
            self.nmodes = 3*self.natoms
            N.divide(self.array, self.weights[N.NewAxis, N.NewAxis, :, :],
                     self.array)
            N.divide(self.array, self.weights[:, :, N.NewAxis, N.NewAxis],
                     self.array)
            self.array.shape = 2*(self.nmodes,)
        else:
            from MMTK_forcefield import SparseForceConstants
            self.natoms = self.universe.numberOfCartesianCoordinates()
            fc = SparseForceConstants(self.natoms, 5*self.natoms)
            eval = self.universe.energyEvaluator()
            energy, g, fc = eval(0, fc, 0)
            self.fc = fc
            self.fc.scale(1./self.weights[:, 0])
        if self.basis is not None:
            _symmetrize(self.array)
            self.array = N.dot(N.dot(self.basis, self.array),
                               N.transpose(self.basis))
            self.nmodes = self.array.shape[0]

    def _diagonalize(self):
        if self.sparse is not None:
            from MMTK_sparseev import sparseMatrixEV
            eigenvalues, eigenvectors = sparseMatrixEV(self.fc, self.nmodes)
            self.array = eigenvectors[:self.nmodes]
            return eigenvalues

        # Calculate eigenvalues and eigenvectors of self.array
        if symeig is not None:
            _symmetrize(self.array)
            ev, modes = symeig(self.array, overwrite=True)
            self.array = N.transpose(modes)
        elif dsyevd is None:
            ev, modes = Heigenvectors(self.array)
            ev = ev.real
            modes = modes.real
            self.array = modes
        else:
            ev = N.zeros((self.nmodes,), N.Float)
            work = N.zeros((1,), N.Float)
            iwork = N.zeros((1,), int_type)
            results = dsyevd('V', 'L', self.nmodes, self.array, self.nmodes,
                             ev, work, -1, iwork, -1, 0)
            lwork = int(work[0])
            liwork = iwork[0]
            work = N.zeros((lwork,), N.Float)
            iwork = N.zeros((liwork,), int_type)
            results = dsyevd('V', 'L', self.nmodes, self.array, self.nmodes,
                             ev, work, lwork, iwork, liwork, 0)
            if results['info'] > 0:
                raise ValueError('Eigenvalue calculation did not converge')

        if self.basis is not None:
            self.array = N.dot(self.array, self.basis)
        return ev

    def _setupBasis(self):
        if type(self.basis) is type(()):
            excluded, basis = self.basis
        else:
            excluded = []
            basis = self.basis
        nexcluded = len(excluded)
        nmodes = len(basis)
        ntotal = nexcluded + nmodes
        natoms = len(basis[0])

        sv = N.zeros((min(ntotal, 3*natoms),), N.Float)
        work_size = N.zeros((1,), N.Float)
        if nexcluded > 0:
            self.basis = N.zeros((ntotal, 3*natoms), N.Float)
            for i in range(nexcluded):
                self.basis[i] = N.ravel(excluded[i].array*self.weights)
            min_n_m = min(3*natoms, nexcluded)
            vt = N.zeros((nexcluded, min_n_m), N.Float)
            iwork = N.zeros((8*min_n_m,), int_type)
            if 3*natoms >= nexcluded:
                result = dgesdd('O', 3*natoms, nexcluded, self.basis,
                                3*natoms, sv, self.basis, 3*natoms, vt, min_n_m,
                                work_size, -1, iwork, 0)
                work = N.zeros((int(work_size[0]),), N.Float)
                result = dgesdd('O', 3*natoms, nexcluded, self.basis,
                                3*natoms, sv, self.basis, 3*natoms, vt, min_n_m,
                                work, work.shape[0], iwork, 0)
            else:
                u = N.zeros((min_n_m, 3*natoms), N.Float)
                result = dgesdd('S', 3*natoms, nexcluded, self.basis,
                                3*natoms, sv, u, 3*natoms, vt, min_n_m,
                                work_size, -1, iwork, 0)
                work = N.zeros((int(work_size[0]),), N.Float)
                result = dgesdd('S', 3*natoms, nexcluded, self.basis,
                                3*natoms, sv, u, 3*natoms, vt, min_n_m,
                                work, work.shape[0], iwork, 0)
                self.basis[:min_n_m] = u
            if result['info'] != 0:
                raise ValueError('Lapack SVD: ' + `result['info']`)
            svmax = N.maximum.reduce(sv)
            nexcluded = N.add.reduce(N.greater(sv, 1.e-10*svmax))
            ntotal = nexcluded + nmodes
            for i in range(nmodes):
                self.basis[i+nexcluded] = N.ravel(basis[i].array*self.weights)
            min_n_m = min(3*natoms, ntotal)
            vt = N.zeros((ntotal, min_n_m), N.Float)
            if 3*natoms >= ntotal:
                result = dgesdd('O', 3*natoms, ntotal, self.basis, 3*natoms,
                                sv, self.basis, 3*natoms, vt, min_n_m,
                                work_size, -1, iwork, 0)
                if int(work_size[0]) > work.shape[0]:
                    work = N.zeros((int(work_size[0]),), N.Float)
                result = dgesdd('O', 3*natoms, ntotal, self.basis, 3*natoms,
                                sv, self.basis, 3*natoms, vt, min_n_m,
                                work, work.shape[0], iwork, 0)
            else:
                u = N.zeros((min_n_m, 3*natoms), N.Float)
                result = dgesdd('S', 3*natoms, ntotal, self.basis, 3*natoms,
                                sv, u, 3*natoms, vt, min_n_m,
                                work_size, -1, iwork, 0)
                if int(work_size[0]) > work.shape[0]:
                    work = N.zeros((int(work_size[0]),), N.Float)
                result = dgesdd('S', 3*natoms, ntotal, self.basis, 3*natoms,
                                sv, u, 3*natoms, vt, min_n_m,
                                work, work.shape[0], iwork, 0)
                self.basis[:min_n_m] = u
            if result['info'] != 0:
                raise ValueError('Lapack SVD: ' + `result['info']`)
            svmax = N.maximum.reduce(sv)
            ntotal = N.add.reduce(N.greater(sv, 1.e-10*svmax))
            nmodes = ntotal - nexcluded
        else:
            if hasattr(self.basis, 'may_modify') and \
               hasattr(self.basis, 'array'):
                self.basis = self.basis.array
            else:
                self.basis = N.array(map(lambda v: v.array, basis))
            N.multiply(self.basis, self.weights, self.basis)
            self.basis.shape = (nmodes, 3*natoms)
            min_n_m = min(3*natoms, nmodes)
            vt = N.zeros((nmodes, min_n_m), N.Float)
            iwork = N.zeros((8*min_n_m,), int_type)
            if 3*natoms >= nmodes:
                result = dgesdd('O', 3*natoms, nmodes, self.basis, 3*natoms,
                                sv, self.basis, 3*natoms, vt, min_n_m,
                                work_size, -1, iwork, 0)
                work = N.zeros((int(work_size[0]),), N.Float)
                result = dgesdd('O', 3*natoms, nmodes, self.basis, 3*natoms,
                                sv, self.basis, 3*natoms, vt, min_n_m,
                                work, work.shape[0], iwork, 0)
            else:
                u = N.zeros((min_n_m, 3*natoms), N.Float)
                result = dgesdd('S', 3*natoms, nmodes, self.basis, 3*natoms,
                                sv, u, 3*natoms, vt, min_n_m,
                                work_size, -1, iwork, 0)
                work = N.zeros((int(work_size[0]),), N.Float)
                result = dgesdd('S', 3*natoms, nmodes, self.basis, 3*natoms,
                                sv, u, 3*natoms, vt, min_n_m,
                                work, work.shape[0], iwork, 0)
                self.basis[:min_n_m] = u
            if result['info'] != 0:
                raise ValueError('Lapack SVD: ' + `result['info']`)
            svmax = N.maximum.reduce(sv)
            nmodes = N.add.reduce(N.greater(sv, 1.e-10*svmax))
            ntotal = nmodes
        self.basis = self.basis[nexcluded:ntotal, :]

#
# Helper functions
#
# Fill in the lower triangle of an upper-triangle symmetric matrix

def _symmetrize(a):
    n = a.shape[0]
    for i in range(n):
        for j in range(i+1, n):
            a[j,i] = a[i,j]
