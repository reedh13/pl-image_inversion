#
# image_inversion ds ChRIS plugin app
#
# (c) 2021 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

from chrisapp.base import ChrisApp
import  os
from    os                  import  listdir
from    os                  import  walk
from    os.path             import  isfile, join, exists
import  sys
import  glob
from PIL import Image, ImageChops
# import  numpy as np
# import  re
# import  time
# import  pudb

# import  pydicom              as      dicom
# import  pylab
# import  matplotlib.cm        as      cm
# import  pfmisc
# from    pfmisc._colors      import  Colors
# from    pfmisc.message      import  Message


Gstr_title = r"""

Generate a title from 
http://patorjk.com/software/taag/#p=display&f=Doom&t=image_inversion

"""

Gstr_synopsis = """

(Edit this in-line help for app specifics. At a minimum, the 
flags below are supported -- in the case of DS apps, both
positional arguments <inputDir> and <outputDir>; for FS and TS apps
only <outputDir> -- and similarly for <in> <out> directories
where necessary.)

    NAME

       image_inversion.py 

    SYNOPSIS

        python image_inversion.py                                         \\
            [-h] [--help]                                               \\
            [--json]                                                    \\
            [--man]                                                     \\
            [--meta]                                                    \\
            [--savejson <DIR>]                                          \\
            [-v <level>] [--verbosity <level>]                          \\
            [--version]                                                 \\
            <inputDir>                                                  \\
            <outputDir> 

    BRIEF EXAMPLE

        * Bare bones execution

            docker run --rm -u $(id -u)                             \
                -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \
                fnndsc/pl-image_inversion image_inversion                        \
                /incoming /outgoing

    DESCRIPTION

        `image_inversion.py` ...

    ARGS

        [-h] [--help]
        If specified, show help message and exit.
        
        [--json]
        If specified, show json representation of app and exit.
        
        [--man]
        If specified, print (this) man page and exit.

        [--meta]
        If specified, print plugin meta data and exit.
        
        [--savejson <DIR>] 
        If specified, save json representation file to DIR and exit. 
        
        [-v <level>] [--verbosity <level>]
        Verbosity level for app. Not used currently.
        
        [--version]
        If specified, print version number and exit. 
"""


class Image_inversion(ChrisApp):
    """
    A plugin to invert the colors of an image.
    """
    PACKAGE                 = __package__
    TITLE                   = 'A ChRIS plugin app'
    CATEGORY                = ''
    TYPE                    = 'ds'
    ICON                    = ''   # url of an icon image
    MIN_NUMBER_OF_WORKERS   = 1    # Override with the minimum number of workers as int
    MAX_NUMBER_OF_WORKERS   = 1    # Override with the maximum number of workers as int
    MIN_CPU_LIMIT           = 1000 # Override with millicore value as int (1000 millicores == 1 CPU core)
    MIN_MEMORY_LIMIT        = 200  # Override with memory MegaByte (MB) limit as int
    MIN_GPU_LIMIT           = 0    # Override with the minimum number of GPUs as int
    MAX_GPU_LIMIT           = 0    # Override with the maximum number of GPUs as int

    # Use this dictionary structure to provide key-value output descriptive information
    # that may be useful for the next downstream plugin. For example:
    #
    # {
    #   "finalOutputFile":  "final/file.out",
    #   "viewer":           "genericTextViewer",
    # }
    #
    # The above dictionary is saved when plugin is called with a ``--saveoutputmeta``
    # flag. Note also that all file paths are relative to the system specified
    # output directory.
    OUTPUT_META_DICT = {}

    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        Use self.add_argument to specify a new app argument.
        """

        self.add_argument('-i', '--inputFile',
                            dest        = 'inputFile',
                            type        = str,
                            optional    = False,
                            help        = 'name of the input file within the inputDir',
                            default     = ''
                        )
        self.add_argument('-t', '--outputFileType',
                            dest        = 'outputFileType',
                            type        = str,
                            default     = '',
                            optional    = True,
                            help        = 'output image file format'
                        )

    

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """

        def mkdir(newdir, mode=0x775):
            """
            works the way a good mkdir should :)
                - already exists, silently complete
                - regular file in the way, raise an exception
                - parent directory(ies) does not exist, make them as well
            """
            if os.path.isdir(newdir):
                pass
            elif os.path.isfile(newdir):
                raise OSError("a file with the same name as the desired " \
                            "dir, '%s', already exists." % newdir)
            else:
                head, tail = os.path.split(newdir)
                if head and not os.path.isdir(head):
                    os.mkdir(head)
                if tail:
                    os.mkdir(newdir)

        print(Gstr_title)
        print('Version: %s' % self.get_version())
        print("Options:", options)
        print("inputdir=", options.inputdir)
        print(os.getcwd())

        inputFile = options.inputFile
        inputFilename = inputFile.split('.')[0]
        inputExtension = inputFile.split('.')[-1]

        # Validate inputFile arg
        if inputExtension not in ['dcm', 'png', 'jpg', 'jpeg']:
            raise ValueError("inputFile must be of type .dcm, .png, .jpg, or .jpeg.")

        # Validate outputFileType arg
        if options.outputFileType == '':
            outputExtension = inputExtension
        elif options.outputFileType not in ['.dcm', '.png', '.jpg', '.jpeg']:
            raise ValueError("outputFileType must be of type .dcm, .png, .jpg, or .jpeg.")
        else:
            outputExtension = options.outputFileType
        
        # Test if file exists
        input_path = options.inputdir + '/' + inputFile
        if not exists(input_path):
            raise ValueError("File not found: " + input_path)

        # Create output folder
        mkdir(options.outputdir)

        # Invert and save image
        # Case for png/jpg/jpeg
        if inputExtension in ['png', 'jpg', 'jpeg']:
            inverted_img = ImageChops.invert(Image.open(input_path))
            inverted_img.save(str(options.outputdir) + '/' + inputFilename + '_inverted' + outputExtension)
        # Case for dcm
        else:
            raise ValueError("DICOM support not implemented yet.")

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)