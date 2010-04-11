from Demo import DemoError
from ChimeraDemo import DemoPanel, DemoParser

##############
#
#  Parsing for old-style demos
#


class DemoParser2065(DemoParser):

    def parseDemo(self):

        f = open(self.src_path, 'r')

        step_num = 0

        while 1:
            line = f.readline()

            if not line:
                break

            if line.strip() == '[INFO]':
                self.parseDemoHeaders(f)

            elif line.strip()[0:6] == '[START':
                step_num += 1
                p = self.parsePanel(f, step_num, line)
                self.demo.demoPanels[step_num] = p



        f.close()

        if step_num == 0:
            raise DemoError("Couldn't find valid panel description in source file. "
                            "Demo must have at least one step.")


    def parseDemoHeaders(self, f):
        import string

        while 1:
            line = f.readline()
            if not line:
                break

            if (line.strip())[0:9] == 'AUTODELAY':
                self.demo.auto_delay = int(line.split()[1])
            elif (line.strip())[0:5] == 'TITLE':
                self.demo.title = string.join(line.split()[1:])
            elif (line.strip())[0:5] == 'IMAGE':
                self.demo.img_src = string.join(line.split()[1:])
            elif (line.strip())[0:8] == 'BG_COLOR':
                self.demo.img_bg_color = string.join(line.split()[1:])
            elif (line.strip())[0:10] == 'AUTORUN_ON':
                self.demo.autorun_on_start = True
            elif (line.strip())[0:4] == 'DESC':
                desc = string.join(line.split()[1:])
                self.demo.description += " " + desc.strip()
            elif line == '' or line.strip()[0:6]  == '[START' :
                raise DemoError("couldn't find \"[END INFO]\" tag.")
            elif line.strip() == '[END INFO]':
                break


    def parsePanel(self, f, step_num, line):

        p = DemoPanel(step_num)

        attrs = self.parseStartAttrs(line)
        if attrs.has_key('AUTODELAY'):
            p.setDelay( int(attrs['AUTODELAY']) )
        if attrs.has_key('TITLE'):
            #print "GOT TITLE"
            p.setTitle( attrs['TITLE'] )

        while 1:
            line = f.readline()
            if not line:
                break

            if line.strip() == '[TEXT]':
                ## parse out the text for this step
                t = self.parseText(f)
                p.setText(t)

            elif line.strip() == '[COMMANDS]':
                ## parse out the commands for this step
                cmds = self.parseCommands(f)
                p.setCmds(cmds)

            elif line.strip() == '[UNDO]':
                undos = self.parseUndo(f)
                p.setUndos(undos)

            elif line.strip() == '[END]':
                return p

            elif line.strip()[0:6] == '[START':
                raise DemoError, "couldn't find \"[END]\" tag for panel #%d." % \
                      (p.getId())


    def parseText(self, f):
        text = ''

        while 1:
            line = f.readline()
            if not line:
                break

            if line.strip() == '[END TEXT]':
                break
            elif line.strip() == '[END]':
                raise DemoError("couldn't find \"[END TEXT]\" tag.")
            else:
                #if line.strip() == '':
                #    text += "\n\n"
                #else:
                text += (" " + line) ## was line.strip()

        return text


    def parseStartAttrs(self, line):
        #print "LINE IS ", line
        attrs = line[6:line.rfind("]")]
        attrs = attrs.strip()

        attr_elts = attrs.split()
        #print "attr_elts is ", attr_elts
        attr_dict = {}
        for elt in attr_elts:
            key,value = elt.split("=")
            attr_dict[key]=value

        return attr_dict

    def parseCommands(self, f):
        cmds = []

        while 1:
            line = f.readline()

            if line.strip() == '[END COMMANDS]':
                break
            elif line == '' or line.strip() == '[END]':
                raise DemoError("couldn't find \"[END COMMANDS]\" tag.")
            else:
                cmds.append( (True, line.strip()) )

        return cmds

    def parseUndo(self, f):
        undos = []

        while 1:
            line = f.readline()

            if line.strip() == '[END UNDO]':
                break
            elif line == '' or line.strip() == '[END]':
                raise DemoError("couldn't find \"[END UNDO]\" tag.")
            else:
                undos.append( (True, line.strip()) )

        return undos


    #
    #
    # End parsing functions for old-style demos
    #
    ###########################3
