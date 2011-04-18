"""
tvat.py: TV Archive Tools 
Author: Force

A collection of tools for sorting and maintaining a TV archive.

"""

import re

regexes = ["^(?P<showname>[\w.-]+?)\.S(?P<season>\d+)\.?E(?P<ep_begin>\d+)([.-]?(S\d+\.?)?E?(?P<ep_end>\d+))?\..*",
           "^(?P<showname>[\w.-]+?)\.(?P<season>\d+)x(?P<ep_begin>\d+).(\d+x(?P<ep_end>\d+)\.)?.*",
           "^(?P<showname>[\w.-]+?)\.Part\.?(?P<ep_begin>\d+)\..*",
           "^(?P<showname>[\w.-]+?)\.(?P<year>(19|20)\d\d)\.(?P<month>[01]\d)\.(?P<day>[0-3]\d)\..*"]
regexes = [re.compile(r) for r in regexes]


def rel_info(rel):
    """
    Extracts the name, season and episodes out of a release name.
    Returns a dictionary with the keys name, season and eps.
    Notice that some releases are multi ep, so eps is a list of all episodes that a release contains
    """
    for r in regexes:
        m = r.match(rel)
        if not m:
            continue
        group = m.groupdict()
        show = {}
        show["name"] = group["showname"]

        if "season" in group:
            show["season"] = int(group["season"])
        elif "year" in group:            
            show["season"] = int(group["year"])
            show["eps"] = [int(group["month"]+group["day"])]
            return show

        if "ep_end" in group and group["ep_end"]:
            begin = int(group["ep_begin"])
            end = int(group["ep_end"])
            show["eps"] = range(begin, end+1)
        else:
            show["eps"] = [int(group["ep_begin"])]
        return show    
    return None
    
    
def main():
    """ This function is just used to test some features of the script """
    rels = ["Tru_Calling.1x14.Daddys_Girl.AC3.DVDRip_XviD-FoV",
        "Animaniacs.S01E310E311.DVDRip.XviD-SAiNTS",
        "Animaniacs.S05E31.DVDRip.XviD-SAiNTS",
        "Buffy.6x05.6x06.Bargaining.AC3.WS_DVDRip_XviD-FoV",
        "Will.and.Grace.S07E10.S07E11.WS.DVDRip.XviD-SAiNTS",
        "Threshold.S01E01-02.DVDRip.XviD-TOPAZ",
        "The.Daily.Show.2010.07.05.Denis.Leary.HDTV.XviD-FQM",
        "Threshold.S01E01-02.HDTV.XviD-TOPAZ",
        "National.Geographic.Drugs.Inc.Part.1.Cocaine.HDTV.XviD-MOMENTUM",
        "Bloody.Foreigners.Part3.The.Untold.Great.Fire.Of.London.iNTERNAL.WS.PDTV.XviD-aAF"]

    eplist = []
    for rel in rels:
        show = rel_info(rel)
        if not show:
            print "failed to parse", rel
            continue
        print show
        if "season" in show and show["season"] > 1900:
            continue
        
        eps = show["eps"]

        for ep in eps:
            if ep in eplist:
                print "zomg, %s has a dupe!" % rel
                break

    
        eplist.extend(eps)


if __name__ == "__main__":
    main()
    
