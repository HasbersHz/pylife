import sys
import ctypes
import typing
from ctypes import c_int as cint
from dataclasses import dataclass

import click

import base.lifealgo as lifealgo
import base.liferender as liferender
import base.util as util
import base.viewport as viewport


start: float = 0
max_time: cint = cint(0)


def time_stamp() -> float:
    global start
    now: float = util.get_time()
    r: float = now - start
    if not start:
        start = now
    elif max_time and r > max_time.value:
        sys.exit(0)
    return r


ViewPort: viewport.Viewport = viewport.Viewport(cint(1000), cint(1000))
imp: lifealgo.LifeAlgo = lifealgo.LifeAlgo()


class NullRender(liferender.LifeRender):
    """This is a "renderer" that is just stubs, for performance testing."""
    def __init__(self):
        pass

    def pix_blit(self, x: cint, y: cint, w: cint, h: cint, pm: str, pm_scale: cint) -> None:
        pass

    def get_colors(self, rgb: tuple[str, str, str], dead_alpha: str, live_alpha: str) -> None:
        dummy: ctypes.c_ubyte = ctypes.c_ubyte()
        self.r = self.g = self.b = dummy
        dead_alpha = live_alpha = chr(255)


renderer: NullRender = NullRender()

# the RuleLoader algo looks for .rule files in the user_rules directory
# then in the supplied_rules directory
user_rules: str = ''
supplied_rules: str = 'Rules/'

benchmark: cint = cint(0)


class ProgErrors(util.BaseLifeErrors):
    """This LifeErrors is used to check rendering during a progress dialog."""
    def __init__(self):
        pass

    def fatal(self, s: str) -> None:
        print("Fatal error:", s, file=sys.stderr)
        sys.exit(10)

    def warning(self, s: str) -> None:
        print("Warning:", s, file=sys.stderr)

    def status(self, s: str) -> None:
        if benchmark.value:
            print(time_stamp(), s)
        else:
            time_stamp()
            print(s)

    def begin_progress(self, s: str) -> None:
        self.abort_progress(0, s)

    def abort_progress(self, frac_done: float, new_msg: str) -> bool:
        imp.draw(ViewPort, renderer)
        return False

    def end_progress(self) -> None:
        self.abort_progress(1, '')

    def get_user_rules(self) -> str:
        return user_rules

    def get_rules_dir(self) -> str:
        return supplied_rules


prog_errors_instance: ProgErrors = ProgErrors()


class STDErrors(util.BaseLifeErrors):
    """This is our standard LifeErrors."""
    def __init__(self):
        pass

    def fatal(self, s: str) -> None:
        print("Fatal error:", s, file=sys.stderr)
        sys.exit(10)

    def warning(self, s: str) -> None:
        print("Warning:", s, file=sys.stderr)

    def status(self, s: str) -> None:
        if benchmark.value:
            print(time_stamp(), s)
        else:
            time_stamp()
            print(s)

    def begin_progress(self, s: str) -> None:
        pass

    def abort_progress(self, frac_done: float, new_msg: str) -> bool:
        return False

    def end_progress(self) -> None:
        pass

    def get_user_rules(self) -> str:
        return user_rules

    def get_rules_dir(self) -> str:
        return supplied_rules


std_errors_instance: STDErrors = STDErrors()

filename: str


@dataclass
class Options:
    short_opt: str
    long_opt: str
    desc: str
    opt_type: str
    data: typing.Any


hyper: cint = cint(0)
hashlife: cint = cint(0)
render, autofit, quiet, pop_count, progress = cint(0), cint(0), cint(0), cint(0), cint(0)
algo_name: str = ''
verbose: cint = cint(0)
timeline: cint = cint(0)
step_thresh: cint = cint(0)
step_factor: cint = cint(0)
life_rule: str = ''
out_filename: str = ''
render_scale: str = '1'
test_script: str = ''
output_gzip, output_is_mc = cint(0), cint(0)
number_offset: cint = cint(0)


@click.command()
@click.option("-m", "--generation", "max_gen",
              help="How far to run",                                    default=-1)
@click.option("-i", "--stepsize",   "inc",
              help="Step size",                                         default=0)
@click.option("-M", "--maxmemory",  "max_mem",
              help="Max memory to use in megabytes",                    default=256)
@click.option("-T", "--maxtime",    "max_time",
              help="Max duration",                                      default=max_time.value)
@click.option("-b", "--benchmark",  "benchmark",
              help="Show timestamps",                                   is_flag=True)
@click.option("-2", "--exponential", "hyper",
              help="Use exponentially increasing steps",                is_flag=True)
@click.option("-q", "--quiet", "quiet",
              help="Don't show population; twice, don't show anything", is_flag=True)
@click.option("-q", "--quiet", "quiet_",                                is_flag=True)
@click.option("-r", "--rule", "life_rule",
              help="Life rule to use",                                  default=life_rule)
@click.option("-s", "--search", "user_rules",
              help="Search directory for .rule files",                  default=user_rules)
@click.option("-h", "--hashlife", "hashlife",
              help="Use Hashlife algorithm",                            is_flag=True)
@click.option("-a", "--algorithm", "algo_name",
              help="Select algorithm by name",                          default=algo_name)
@click.option("-o", "--output", "out_filename",
              help="Output file (*.rle, *.mc, *.rle.gz, *.mc.gz)",      default=out_filename)
@click.option("-v", "--verbose", "verbose",
              help="Verbose",                                           is_flag=True)
@click.option("-t", "--timeline", "timeline",
              help="Use timeline",                                      is_flag=True)
@click.option("--render", "render", help="Render (benchmarking)",       is_flag=True)
@click.option("--progress", "progress",
              help="Render during progress dialog (debugging)",         is_flag=True)
@click.option("--popcount", "pop_count",
              help="Popcount (benchmarking)",                           is_flag=True)
@click.option("--scale", "render_scale", help="Rendering scale",        default=render_scale)
# @click.option("--stepthreshold", "step_thresh",
#               help="Stepsize >= gencount/this (default 1)",             default=step_thresh.value)
# @click.option("--stepfactor", "step_factor",
#               help="How much to scale step by (default 2)",             default=step_factor.value)
@click.option("--autofit", "autofit",
              help="Autofit before each render",                        is_flag=True)
@click.option("--exec", "test_script",
              help="Run testing script",                                default=test_script)
@click.argument("patternfile", required=False)
def main(max_gen, inc, max_mem, max_time, benchmark, hyper, quiet, quiet_, life_rule, user_rules, hashlife, algo_name,
         out_filename, verbose, timeline, render, progress, pop_count, render_scale,  # step_thresh, step_factor,
         autofit, test_script, patternfile,
         ):
    ...


def ends_with(s: str, suff: str) -> bool:
    return s.endswith(suff)


def usage(s: str):
    pass


MAXRLE: int = 1000000000


def writepat(fc: cint) -> None:
    this_filename: str = out_filename
    tmp_filename: str = ''
    if fc.value >= 0:
        tmp_filename = out_filename
        p: str = tmp_filename + number_offset

"""
#define STRINGIFY(ARG) STR2(ARG)
#define STR2(ARG) #ARG
#define MAXRLE 1000000000
void writepat(int fc) {
   char *thisfilename = outfilename ;
   char tmpfilename[256] ;
   if (fc >= 0) {
      strcpy(tmpfilename, outfilename) ;
      char *p = tmpfilename + numberoffset ;
      *p++ = '-' ;
      sprintf(p, "%d", fc) ;
      p += strlen(p) ;
      strcpy(p, outfilename + numberoffset) ;
      thisfilename = tmpfilename ;
   }
   cerr << "(->" << thisfilename << flush ;
   bigint t, l, b, r ;
   imp->findedges(&t, &l, &b, &r) ;
   if (!outputismc && (t < -MAXRLE || l < -MAXRLE || b > MAXRLE || r > MAXRLE))
      lifefatal("Pattern too large to write in RLE format") ;
   const char *err = writepattern(thisfilename, *imp,
                                  outputismc ? MC_format : RLE_format,
                                  outputgzip ? gzip_compression : no_compression,
                                  t.toint(), l.toint(), b.toint(), r.toint()) ;
   if (err != 0)
      lifewarning(err) ;
   cerr << ")" << flush ;
}

const int MAXCMDLENGTH = 2048 ;
struct cmdbase {
   cmdbase(const char *cmdarg, const char *argsarg) {
      verb = cmdarg ;
      args = argsarg ;
      next = list ;
      list = this ;
   }
   const char *verb ;
   const char *args ;
   int iargs[4] ;
   char *sarg ;
   bigint barg ;
   virtual void doit() {}
   // for convenience, we put the generic loop here that takes a
   // 4x bounding box and runs getnext on all y values until
   // they are done.  Input is assumed to be a bounding box in the
   // form minx miny maxx maxy
   void runnextloop() {
      int minx = iargs[0] ;
      int miny = iargs[1] ;
      int maxx = iargs[2] ;
      int maxy = iargs[3] ;
      int v ;
      for (int y=miny; y<=maxy; y++) {
         for (int x=minx; x<=maxx; x++) {
            int dx = imp->nextcell(x, y, v) ;
            if (dx < 0)
               break ;
            if (x > 0 && (x + dx) < 0)
               break ;
            x += dx ;
            if (x > maxx)
               break ;
            nextloopinner(x, y) ;
         }
      }
   }
   virtual void nextloopinner(int, int) {}
   int parseargs(const char *cmdargs) {
      int iargn = 0 ;
      char sbuf[MAXCMDLENGTH+2] ;
      for (const char *rargs = args; *rargs; rargs++) {
         while (*cmdargs && *cmdargs <= ' ')
            cmdargs++ ;
         if (*cmdargs == 0) {
            lifewarning("Missing needed argument") ;
            return 0 ;
         }
         switch (*rargs) {
         case 'i':
           if (sscanf(cmdargs, "%d", iargs+iargn) != 1) {
             lifewarning("Missing needed integer argument") ;
             return 0 ;
           }
           iargn++ ;
           break ;
         case 'b':
           {
              int i = 0 ;
              for (i=0; cmdargs[i] > ' '; i++)
                 sbuf[i] = cmdargs[i] ;
              sbuf[i] = 0 ;
              barg = bigint(sbuf) ;
           }
           break ;
         case 's':
           if (sscanf(cmdargs, "%s", sbuf) != 1) {
             lifewarning("Missing needed string argument") ;
             return 0 ;
           }
           sarg = strdup(sbuf) ;
           break ;
         default:
           lifefatal("Internal error in parseargs") ;
         }
         while (*cmdargs && *cmdargs > ' ')
           cmdargs++ ;
      }
      return 1 ;
   }
   static void docmd(const char *cmdline) {
      for (cmdbase *cmd=list; cmd; cmd = cmd->next)
         if (strncmp(cmdline, cmd->verb, strlen(cmd->verb)) == 0 &&
             cmdline[strlen(cmd->verb)] <= ' ') {
            if (cmd->parseargs(cmdline+strlen(cmd->verb))) {
               cmd->doit() ;
            }
            return ;
         }
      lifewarning("Didn't understand command") ;
   }
   cmdbase *next ;
   virtual ~cmdbase() {}
   static cmdbase *list ;
} ;

cmdbase *cmdbase::list = 0 ;

struct loadcmd : public cmdbase {
   loadcmd() : cmdbase("load", "s") {}
   virtual void doit() {
     const char *err = readpattern(sarg, *imp) ;
     if (err != 0)
       lifewarning(err) ;
   }
} load_inst ;
struct stepcmd : public cmdbase {
   stepcmd() : cmdbase("step", "b") {}
   virtual void doit() {
      if (imp->unbounded && (imp->gridwd > 0 || imp->gridht > 0)) {
         // bounded grid, so must step by 1
         imp->setIncrement(1) ;
         if (!imp->CreateBorderCells()) exit(10) ;
         imp->step() ;
         if (!imp->DeleteBorderCells()) exit(10) ;
      } else {
         imp->setIncrement(barg) ;
         imp->step() ;
      }
      if (timeline) imp->extendtimeline() ;
      cout << imp->getGeneration().tostring() << ": " ;
      cout << imp->getPopulation().tostring() << endl ;
   }
} step_inst ;
struct showcmd : public cmdbase {
   showcmd() : cmdbase("show", "") {}
   virtual void doit() {
      cout << imp->getGeneration().tostring() << ": " ;
      cout << imp->getPopulation().tostring() << endl ;
   }
} show_inst ;
struct quitcmd : public cmdbase {
   quitcmd() : cmdbase("quit", "") {}
   virtual void doit() {
      cout << "Buh-bye!" << endl ;
      exit(10) ;
   }
} quit_inst ;
struct setcmd : public cmdbase {
   setcmd() : cmdbase("set", "ii") {}
   virtual void doit() {
      imp->setcell(iargs[0], iargs[1], 1) ;
   }
} set_inst ;
struct unsetcmd : public cmdbase {
   unsetcmd() : cmdbase("unset", "ii") {}
   virtual void doit() {
      imp->setcell(iargs[0], iargs[1], 0) ;
   }
} unset_inst ;
struct helpcmd : public cmdbase {
   helpcmd() : cmdbase("help", "") {}
   virtual void doit() {
      for (cmdbase *cmd=list; cmd; cmd = cmd->next)
         cout << cmd->verb << " " << cmd->args << endl ;
   }
} help_inst ;
struct getcmd : public cmdbase {
   getcmd() : cmdbase("get", "ii") {}
   virtual void doit() {
     cout << "At " << iargs[0] << "," << iargs[1] << " -> " <<
        imp->getcell(iargs[0], iargs[1]) << endl ;
   }
} get_inst ;
struct getnextcmd : public cmdbase {
   getnextcmd() : cmdbase("getnext", "ii") {}
   virtual void doit() {
     int v ;
     cout << "At " << iargs[0] << "," << iargs[1] << " next is " <<
        imp->nextcell(iargs[0], iargs[1], v) << endl ;
   }
} getnext_inst ;
vector<pair<int, int> > cutbuf ;
struct copycmd : public cmdbase {
   copycmd() : cmdbase("copy", "iiii") {}
   virtual void nextloopinner(int x, int y) {
      cutbuf.push_back(make_pair(x-iargs[0], y-iargs[1])) ;
   }
   virtual void doit() {
      cutbuf.clear() ;
      runnextloop() ;
      cout << cutbuf.size() << " pixels copied." << endl ;
   }
} copy_inst ;
struct cutcmd : public cmdbase {
   cutcmd() : cmdbase("cut", "iiii") {}
   virtual void nextloopinner(int x, int y) {
      cutbuf.push_back(make_pair(x-iargs[0], y-iargs[1])) ;
      imp->setcell(x, y, 0) ;
   }
   virtual void doit() {
      cutbuf.clear() ;
      runnextloop() ;
      cout << cutbuf.size() << " pixels cut." << endl ;
   }
} cut_inst ;
// this paste only sets cells, never clears cells
struct pastecmd : public cmdbase {
   pastecmd() : cmdbase("paste", "ii") {}
   virtual void doit() {
      for (unsigned int i=0; i<cutbuf.size(); i++)
         imp->setcell(cutbuf[i].first, cutbuf[i].second, 1) ;
      cout << cutbuf.size() << " pixels pasted." << endl ;
   }
} paste_inst ;
struct showcutcmd : public cmdbase {
   showcutcmd() : cmdbase("showcut", "") {}
   virtual void doit() {
      for (unsigned int i=0; i<cutbuf.size(); i++)
         cout << cutbuf[i].first << " " << cutbuf[i].second << endl ;
   }
} showcut_inst ;

lifealgo *createUniverse() {
   if (algoName == 0) {
     if (hashlife)
       algoName = (char *)"HashLife" ;
     else
       algoName = (char *)"QuickLife" ;
   } else if (strcmp(algoName, "RuleTable") == 0 ||
              strcmp(algoName, "RuleTree") == 0) {
       // RuleTable and RuleTree algos have been replaced by RuleLoader
       algoName = (char *)"RuleLoader" ;
   }
   staticAlgoInfo *ai = staticAlgoInfo::byName(algoName) ;
   if (ai == 0) {
      cout << algoName << endl ; //!!!
      lifefatal("No such algorithm") ;
   }
   lifealgo *imp = (ai->creator)() ;
   if (imp == 0)
      lifefatal("Could not create universe") ;
   imp->setMaxMemory(maxmem) ;
   return imp ;
}

struct newcmd : public cmdbase {
   newcmd() : cmdbase("new", "") {}
   virtual void doit() {
     if (imp != 0)
        delete imp ;
     imp = createUniverse() ;
   }
} new_inst ;
struct sethashingcmd : public cmdbase {
   sethashingcmd() : cmdbase("sethashing", "i") {}
   virtual void doit() {
      hashlife = iargs[0] ;
   }
} sethashing_inst ;
struct setmaxmemcmd : public cmdbase {
   setmaxmemcmd() : cmdbase("setmaxmem", "i") {}
   virtual void doit() {
      maxmem = iargs[0] ;
   }
} setmaxmem_inst ;
struct setalgocmd : public cmdbase {
   setalgocmd() : cmdbase("setalgo", "s") {}
   virtual void doit() {
      algoName = sarg ;
   }
} setalgocmd_inst ;
struct edgescmd : public cmdbase {
   edgescmd() : cmdbase("edges", "") {}
   virtual void doit() {
      bigint t, l, b, r ;
      imp->findedges(&t, &l, &b, &r) ;
      cout << "Bounding box " << l.tostring() ;
      cout << " " << t.tostring() ;
      cout << " .. " << r.tostring() ;
      cout << " " << b.tostring() << endl ;
   }
} edges_inst ;

void runtestscript(const char *testscript) {
   FILE *cmdfile = 0 ;
   if (strcmp(testscript, "-") != 0)
      cmdfile = fopen(testscript, "r") ;
   else
      cmdfile = stdin ;
   char cmdline[MAXCMDLENGTH + 10] ;
   if (cmdfile == 0)
      lifefatal("Cannot open testscript") ;
   for (;;) {
     cerr << flush ;
     if (cmdfile == stdin)
       cout << "bgolly> " << flush ;
     else
       cout << flush ;
     if (fgets(cmdline, MAXCMDLENGTH, cmdfile) == 0)
        break ;
     cmdbase::docmd(cmdline) ;
   }
   exit(0) ;
}

int main(int argc, char *argv[]) {
   cout << "This is bgolly " STRINGIFY(VERSION) " Copyright 2005-2022 The Golly Gang."
        << endl ;
   cout << "-" ;
   for (int i=0; i<argc; i++)
      cout << " " << argv[i] ;
   cout << endl << flush ;
   qlifealgo::doInitializeAlgoInfo(staticAlgoInfo::tick()) ;
   hlifealgo::doInitializeAlgoInfo(staticAlgoInfo::tick()) ;
   generationsalgo::doInitializeAlgoInfo(staticAlgoInfo::tick()) ;
   ltlalgo::doInitializeAlgoInfo(staticAlgoInfo::tick()) ;
   jvnalgo::doInitializeAlgoInfo(staticAlgoInfo::tick()) ;
   superalgo::doInitializeAlgoInfo(staticAlgoInfo::tick()) ;
   ruleloaderalgo::doInitializeAlgoInfo(staticAlgoInfo::tick()) ;
   while (argc > 1 && argv[1][0] == '-') {
      argc-- ;
      argv++ ;
      char *opt = argv[0] ;
      int hit = 0 ;
      for (int i=0; options[i].shortopt; i++) {
        if (strcmp(opt, options[i].shortopt) == 0 ||
            strcmp(opt, options[i].longopt) == 0) {
          switch (options[i].opttype) {
case 'i':
             if (argc < 2)
                lifefatal("Bad option argument") ;
             *(int *)options[i].data = atol(argv[1]) ;
             argc-- ;
             argv++ ;
             break ;
case 'I':
             if (argc < 2)
                lifefatal("Bad option argument") ;
             *(bigint *)options[i].data = bigint(argv[1]) ;
             argc-- ;
             argv++ ;
             break ;
case 'b':
             (*(int *)options[i].data) += 1 ;
             break ;
case 's':
             if (argc < 2)
                lifefatal("Bad option argument") ;
             *(char **)options[i].data = argv[1] ;
             argc-- ;
             argv++ ;
             break ;
          }
          hit++ ;
          break ;
        }
      }
      if (!hit)
         usage("Bad option given") ;
   }
   if (argc < 2 && !testscript)
      usage("No pattern argument given") ;
   if (argc > 2)
      usage("Extra stuff after pattern argument") ;
   if (outfilename) {
      if (endswith(outfilename, ".rle")) {
      } else if (endswith(outfilename, ".mc")) {
         outputismc = 1 ;
#ifdef ZLIB
      } else if (endswith(outfilename, ".rle.gz")) {
         outputgzip = 1 ;
      } else if (endswith(outfilename, ".mc.gz")) {
         outputismc = 1 ;
         outputgzip = 1 ;
#endif
      } else {
         lifefatal("Output filename must end with .rle or .mc.") ;
      }
      if (strlen(outfilename) > 200)
         lifefatal("Output filename too long") ;
   }
   if (timeline && hyperxxx)
      lifefatal("Cannot use both timeline and exponentially increasing steps") ;
   imp = createUniverse() ;
   if (progress)
      lifeerrors::seterrorhandler(&progerrors_instance) ;
   else
      lifeerrors::seterrorhandler(&stderrors_instance) ;
   if (verbose) {
      hlifealgo::setVerbose(1) ;
   }
   imp->setMaxMemory(maxmem) ;
   timestamp() ;
   if (testscript) {
      if (argc > 1) {
         filename = argv[1] ;
         const char *err = readpattern(argv[1], *imp) ;
         if (err) lifefatal(err) ;
      }
      runtestscript(testscript) ;
   }
   filename = argv[1] ;
   const char *err = readpattern(argv[1], *imp) ;
   if (err) lifefatal(err) ;
   if (liferule) {
      err = imp->setrule(liferule) ;
      if (err) lifefatal(err) ;
   }
   bool boundedgrid = imp->unbounded && (imp->gridwd > 0 || imp->gridht > 0) ;
   if (boundedgrid) {
      if (hyperxxx || inc > 1)
         lifewarning("Step size must be 1 for a bounded grid") ;
      hyperxxx = 0 ;
      inc = 1 ;     // only step by 1
   }
   if (inc != 0)
      imp->setIncrement(inc) ;
   if (timeline) {
      int lowbit = inc.lowbitset() ;
      bigint t = 1 ;
      for (int i=0; i<lowbit; i++)
         t.mul_smallint(2) ;
      if (t != inc)
         lifefatal("Bad increment for timeline") ;
      imp->startrecording(2, lowbit) ;
   }
   int fc = 0 ;
   for (;;) {
      if (benchmark)
         cout << timestamp() << " " ;
      else
         timestamp() ;
      if (quiet < 2) {
         cout << imp->getGeneration().tostring() ;
         if (!quiet) {
            const char *s = imp->getPopulation().tostring() ;
            if (benchmark) {
               cout << endl ;
               cout << timestamp() << " pop " << s << endl ;
            } else {
               cout << ": " << s << endl ;
            }
         } else
            cout << endl ;
      }
      if (popcount)
         imp->getPopulation() ;
      if (autofit)
        imp->fit(viewport, 1) ;
      if (render)
        imp->draw(viewport, renderer) ;
      if (maxgen >= 0 && imp->getGeneration() >= maxgen)
         break ;
      if (!hyperxxx && maxgen > 0 && inc == 0) {
         bigint diff = maxgen ;
         diff -= imp->getGeneration() ;
         int bs = diff.lowbitset() ;
         diff = 1 ;
         diff <<= bs ;
         imp->setIncrement(diff) ;
      }
      if (boundedgrid && !imp->CreateBorderCells()) break ;
      imp->step() ;
      if (boundedgrid && !imp->DeleteBorderCells()) break ;
      if (timeline) imp->extendtimeline() ;
      if (maxgen < 0 && outfilename != 0)
         writepat(fc++) ;
      if (timeline && imp->getframecount() + 2 > MAX_FRAME_COUNT)
         imp->pruneframes() ;
      if (hyperxxx)
         imp->setIncrement(imp->getGeneration()) ;
   }
   if (maxgen >= 0 && outfilename != 0)
      writepat(-1) ;
   exit(0) ;
}
"""

if __name__ == '__main__':
    main()
