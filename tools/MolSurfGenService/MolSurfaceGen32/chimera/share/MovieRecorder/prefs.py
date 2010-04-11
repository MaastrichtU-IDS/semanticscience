from chimera import preferences

LICENSE_AGREE =  "accepted license agreement"

options = {
    LICENSE_AGREE: False
    }

prefs = preferences.addCategory("Movie Recorder",
                                preferences.HiddenCategory,
                                optDict = options
                                )
