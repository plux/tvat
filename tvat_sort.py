#!/usr/bin/env python
import os
import re
import shutil
from sys import stderr, argv
import ConfigParser
from datetime import date
from tvat import rel_info
from os import path


def print_error(x, *args):
    stderr.write("%s: " % path.basename(__file__))
    stderr.write(x % args)
    stderr.write("\n")

def sort_rels(inc_dir, arch_dir, config):
    arch_shows = os.listdir(arch_dir)
    count = 0
    for rel in os.listdir(inc_dir):
        move_from = path.join(inc_dir,rel)
        try:
            rel_stat = os.stat(move_from)
        except:
            print_error("Failed to stat %s", move_from)
            continue

        rel_date = date.fromtimestamp(rel_stat.st_mtime)
        days_ago = (date.today() - rel_date).days

        if days_ago < config.getint('general','move_age'):
            continue             # Don't move unless release is old
        
        show = rel_info(rel)
        if not show:
            continue

        for arch_show in arch_shows:
            if arch_show.lower() == show["name"].lower():
                show_path = path.join(arch_dir, arch_show)
                if "season" not in show:                        
                    season_path = show_path
                elif show["season"] > 1900:
                    season_path = path.join(show_path, "%02i" % show["season"])
                else:
                    season_path = path.join(show_path, "S%02i" % show["season"])

                move_to = path.join(season_path, rel)                

                if config.getboolean('general', 'debug'):
                    print "Moving %s to archive..." % rel

                if not config.getboolean('general', 'test'):
                    usr_grp = config.get('general','usr_grp')
                    if not(os.access(season_path, os.F_OK)):
                        os.mkdir(season_path)
                        os.system("chown -R %s %s" % (usr_grp, season_path))
                        os.system("chmod -R 777 %s" % season_path)
                    try:
                        shutil.move(move_from, move_to)
                        os.system("chown -R %s %s" % (usr_grp, move_to))
                        os.system("chmod -R 777 %s" % move_to)
                    except:
                        if os.access(move_to, os.F_OK):
                            print_error("%s is already in archive (%s), removing %s.", rel, move_to, move_from)
                            try:
                                shutil.rmtree(move_from)
                            except:
                                print_error("Failed to remove %s", move_from)
                        else:
                            print_error("Failed to move %s to %s", move_from, move_to)

                if config.getboolean('general', 'debug'):
                    print "...Done."
                count = count + 1
            
    return count

def main():
    if len(argv) > 1:
        configfile = argv[1] 
    else:
        configfile = 'tvat_sort.conf'

    config = ConfigParser.ConfigParser()

    if config.read([configfile]) == []:
        print_error("Unable to load config %s.", configfile)
        return

    if not config.getboolean('general', 'enable'):
        print_error("Script has been disabled.")
        return

    dirs = []
    for line in config.get('general','dirs').split('\n'):
        (inc, arch) = line.split(':')
        dirs.append((inc.strip(), arch.strip()))
    
    count = sum([sort_rels(inc, arch, config) for (inc,arch) in dirs])

    if not config.getboolean('general', 'debug'):
        return

    if count > 0:
        print "All done. Moved %s releases." % count
    else:
        print "Found nothing to move"

if __name__ == "__main__":
    main()
