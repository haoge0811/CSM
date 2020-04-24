# author: Eda Yan <yidayan@usc.edu>

def float2string(s):
    ss = str(s)
    if ss[-3:] == 'e-3':
        ss = ss.replace('e-3', 'm')
    elif ss[-3:] == 'e-4':
        ss = ss.replace('e-4','')
        ss = str(float(ss) * 100)+'u'
    elif ss[-3:] == 'e-5':
        ss = ss.replace('e-5','')
        ss = str(float(ss) * 10)+'u'
    elif ss[-3:] == 'e-6':
        ss = ss.replace('e-6', 'u')
    elif ss[-3:] == 'e-7':
        ss = ss.replace('e-7','')
        ss = str(float(ss) * 100)+'n'
    elif ss[-3:] == 'e-8':
        ss = ss.replace('e-8','')
        ss = str(float(ss) * 10)+'n'
    elif ss[-3:] == 'e-9':
        ss = ss.replace('e-9', 'n')
    elif ss[-4:] == 'e-10':
        ss = ss.replace('e-10','')
        ss = str(float(ss) * 100)+'p'
    elif ss[-4:] == 'e-11':
        ss = ss.replace('e-11','')
        ss = str(float(ss) * 10)+'p'
    elif ss[-4:] == 'e-12':
        ss = ss.replace('e-12', 'p')
    elif ss[-4:] == 'e-13':
        ss = ss.replace('e-13','')
        ss = str(float(ss) * 100)+'f'
    elif ss[-4:] == 'e-14':
        ss = ss.replace('e-14','')
        ss = str(float(ss) * 10)+'f'
    elif ss[-4:] == 'e-15':
        ss = ss.replace('e-15', 'f')
    elif ss[-4:] == 'e-16':
        ss = ss.replace('e-16','')
        ss = str(float(ss) * 100)+'a'
    elif ss[-4:] == 'e-17':
        ss = ss.replace('e-17','')
        ss = str(float(ss) * 10)+'a'
    elif ss[-4:] == 'e-18':
        ss = ss.replace('e-18', 'a')
    return ss
    
def string2float(s):
    if s[-1] == 'm':
        s = s.replace('m', 'e-3')
    elif s[-1] == 'u':
        s = s.replace('u', 'e-6')
    elif s[-1] == 'n':
        s = s.replace('n', 'e-9')
    elif s[-1] == 'p':
        s = s.replace('p', 'e-12')
    elif s[-1] == 'f':
        s = s.replace('f', 'e-15')
    elif s[-1] == 'a':
        s = s.replace('a', 'e-18')
    return float(s)


def generate_from_template(template_directory, output_directory, replace):
    infile  = open(template_directory, "r")
    outfile = open(output_directory, "w", buffering=0)

    for line in infile:
        if "$$" in line:      # if this line is to be replaced
            for k in replace:    # if an item is listed in input dictionary
                if k in line: # then replace it with the dictionary value
                    line = line.replace(k, str(replace[k]))
        if ".subckt" in line:
            line = line.replace(' n1 ', ' ')
        outfile.write(line)

    infile.close()
    outfile.close()

def print_header():
    print "   _____    _____   __  __ "  
    print "  / ____|  / ____| |  \/  |" 
    print " | |      | (___   | \  / |" 
    print " | |       \___ \  | |\/| |" 
    print " | |____   ____) | | |  | |" 
    print "  \_____| |_____/  |_|  |_|" 
    print "      By USC SPORT-LAB    \n\n" 
                           

def print_header2():
    print " ______       ______       __       ___"
    print "/$$$$$$\      $$$$$$\      $$\      $$ |" 
    print "|$$$$$$$\    $$  __$$\     $$$\    $$$ |" 
    print "|$$/  \_|    $$ /  \__|    $$$$\  $$$$ |"
    print "|$$|         \$$$$$$\      $$\$$\$$ $$ |"
    print "|$$|          \____$$\     $$ \$$$  $$ |"
    print "|$$|  $$\    $$\   $$ |    $$ |\$  /$$ |"
    print "\$$$$$$ |    \$$$$$$  |    $$ | \_/ $$ |"
    print " \_____/     \______/     \__|     \__|"