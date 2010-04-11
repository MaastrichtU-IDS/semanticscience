import chimera.extension
import Demo

class Myo_Demo_EMO(chimera.extension.EMO):
    def name(self):
        return 'Myoglobin Demo'
    def description(self):
        return 'Derived from Susan\'s Myoglobin demo '
    def categories(self):
        return ['Demos']
    def icon(self):
        return None
    def activate(self):
        self.module().startDemo('Myoglobin_Demo')

class COX_Demo_EMO(chimera.extension.EMO):
    def name(self):
        return 'COX Inhibitors Demo'
    def description(self):
        return 'Selective inhibition of cyclooxygenases'
    def categories(self):
        return ['Demos']
    def icon(self):
        return None
    def activate(self):
        self.module().startDemo('COX_Demo')

class FSH_Demo_EMO(chimera.extension.EMO):
    def name(self):
        return 'Hormone-Receptor Complex Demo'
    def description(self):
        return 'The structure of human follicle-stimulating hormone (FSH) and its receptor'
    def categories(self):
        return ['Demos']
    def icon(self):
        return None
    def activate(self):
        self.module().startDemo('FSH_Demo')

class About_Demo_EMO(chimera.extension.EMO):
    def name(self):
        return 'About Demos'
    def description(self):
        return 'About Chimera\'s demo feature'
    def categories(self):
        return ['Demos']
    def icon(self):
        return None
    def activate(self):
        from chimera import dialogs
        dialogs.display(self.module().AboutDemosDialog.name)

class DemoEMO(chimera.extension.EMO):
    def name(self):
        return 'Open Demo...'
    def description(self):
        return 'Open and play demonstration'
    def categories(self):
        return ['Demos']
    def icon(self):
        return None
    def activate(self):
        self.module().chooseDemo()
        return None

class DemoEditorEMO(chimera.extension.EMO):
    def name(self):
        return 'Demo Editor'
    def description(self):
        return 'Open demo editing tool'
    def categories(self):
        return ['Demos']
    def icon(self):
        return None
    def activate(self):
        self.module().showDemoEditor()
        return None
    
#chimera.extension.manager.registerExtension(Myo_Demo_EMO(__file__))
chimera.extension.manager.registerExtension(COX_Demo_EMO(__file__))
chimera.extension.manager.registerExtension(FSH_Demo_EMO(__file__))
#chimera.extension.manager.registerExtension(DemoEMO(__file__))
chimera.extension.manager.registerExtension(About_Demo_EMO(__file__))
chimera.extension.manager.registerExtension(DemoEditorEMO(__file__))
