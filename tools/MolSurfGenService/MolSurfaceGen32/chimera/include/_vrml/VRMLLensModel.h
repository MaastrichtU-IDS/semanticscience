#ifndef Chimera_VRMLLensModel_h
# define Chimera_VRMLLensModel_h

# ifndef WrapPy

# include <_chimera/LensModel.h>
# include <set>

extern "C" {
typedef struct _object PyObject;
}

namespace chimera {

class Lens;
class Model;

} // namespace VRML

namespace VRML {

class VRMLModel;

class VRMLLensModel: public chimera::LensModel {
public:
	VRMLLensModel(chimera::Lens *lens, VRMLModel *vrml);
	virtual void	draw(const chimera::LensViewer *viewer,
				chimera::LensViewer::DrawPass pass) const;
	virtual void	drawPick(const chimera::LensViewer *viewer) const;
	virtual void	invalidateCache();
	virtual void	invalidateSelection();

	chimera::Model	*model() const;

	virtual void	x3dWrite(std::ostream &out, unsigned indent,
					chimera::X3DScene *info) const;

private:
	virtual		~VRMLLensModel();
	VRMLModel	*vrml;

	void		updateModel(const chimera::NotifierReason &);
	class ModelNotifier: public chimera::Notifier {
	public:
		void update(const void *tag, void *,
				const chimera::NotifierReason &reason) const {
			VRMLLensModel *vrmllm = static_cast<VRMLLensModel *>
						(const_cast<void *>(tag));
			vrmllm->updateModel(reason);
		}
	};
	friend class ModelNotifier;
	ModelNotifier	modelNotifier;
	mutable bool	reportedError;
};

} // namespace chimera

# endif /* WrapPy */

#endif
