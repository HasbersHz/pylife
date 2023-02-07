import numpy as np
import numba as nb
import ctypes as ct
from dataclasses import dataclass
from numba.experimental import jitclass
from lifealgo import *
from lifepoll import LifePoll
from cffi import FFI



"""
# @jitclass
@dataclass()
class Brick:  # 64 bytes
    d = np.zeros(16, np.uint)


# @jitclass
@dataclass()
class Tile:  # 32 bytes
    b = np.array(4 * (Brick(),))
    c = np.array(6 * (np.short(),))
    flags = cint()
    local_delta_forward = cint()


@dataclass()
class SuperTile:  # 44 bytes
    d = np.array(8 * (Tile(),))
    flags = cint()
    pop = np.array((cint(), cint()))
"""


class HQLifeAlgo(LifeAlgo):
    def __init__(self):
        super(HQLifeAlgo, self).__init__()

    def set_cell(self, x: cint, y: cint, new_state: cint) -> cint:
        pass

    def get_cell(self, x: cint, y: cint) -> cint:
        pass

    def next_cell(self, x: cint, y: cint, v: cint) -> cint:
        pass

    def end_of_pattern(self):
        """call after set_cell calls"""


"""    virtual void endofpattern() {
        poller->bailIfCalculating() ;
    popValid = 0 ;
    }
    virtual void setIncrement(bigint inc) { increment = inc ; }
    virtual void setIncrement(int inc) { increment = inc ; }
    virtual void setGeneration(bigint gen) { generation = gen ; }
    virtual const bigint &getPopulation() ;
    virtual int isEmpty() ;
    // can we do the gen count doubling? only hashlife
    virtual int hyperCapable() { return 0 ; }
    virtual void setMaxMemory(int m) ;
    virtual int getMaxMemory() { return (int)(maxmemory >> 20) ; }
    virtual const char *setrule(const char *s) ;
    virtual const char *getrule() { return qliferules.getrule() ; }
    virtual void step() ;
    virtual void* getcurrentstate() { return 0 ; }
    virtual void setcurrentstate(void *) {}
    virtual void draw(viewport &view, liferender &renderer) ;
    virtual void fit(viewport &view, int force) ;
    virtual void lowerRightPixel(bigint &x, bigint &y, int mag) ;
    virtual void findedges(bigint *t, bigint *l, bigint *b, bigint *r) ;
    virtual const char *writeNativeFormat(std::ostream &, char *) {
    return "No native format for qlifealgo yet." ;
}
static void doInitializeAlgoInfo(staticAlgoInfo &) ;
private:
linkedmem *filllist(int size) ;
brick *newbrick() ;
tile *newtile() ;
supertile *newsupertile(int lev) ;
void uproot() ;
int doquad01(supertile *zis, supertile *edge,
supertile *par, supertile *cor, int lev) ;
int doquad10(supertile *zis, supertile *edge,
supertile *par, supertile *cor, int lev) ;
int p01(tile *p, tile *pr, tile *pd, tile *prd) ;
int p10(tile *plu, tile *pu, tile *pl, tile *p) ;
G_INT64 find_set_bits(supertile *p, int lev, int gm1) ;
int isEmpty(supertile *p, int lev, int gm1) ;
supertile *mdelete(supertile *p, int lev) ;
G_INT64 popcount() ;
int uproot_needed() ;
void dogen() ;
void renderbm(int x, int y) ;
void renderbm(int x, int y, int xsize, int ysize) ;
void BlitCells(supertile *p, int xoff, int yoff, int wd, int ht, int lev) ;
void ShrinkCells(supertile *p, int xoff, int yoff, int wd, int ht, int lev) ;
int nextcell(int x, int y, supertile *n, int lev) ;
void fill_ll(int d) ;
int lowsub(vector<supertile*> &src, vector<supertile*> &dst, int lev) ;
int highsub(vector<supertile*> &src, vector<supertile*> &dst, int lev) ;
void allsub(vector<supertile*> &src, vector<supertile*> &dst, int lev) ;
int gethbitsfromleaves(vector<supertile *> v) ;
int getvbitsfromleaves(vector<supertile *> v) ;
supertile *markglobalchange(supertile *, int, int &) ;
void markglobalchange() ; // call if the rule changes
                                              /* data elements */
                                                      int min, max, rootlev ;
int minlow32 ;
bigint bmin, bmax ;
bigint population ;
int popValid ;
linkedmem *tilelist, *supertilelist, *bricklist ;
linkedmem *memused ;
brick *emptybrick ;
tile *emptytile ;
supertile *root, *nullroot, *nullroots[40] ;
int cleandowncounter ;
g_uintptr_t maxmemory, usedmemory ;
char *ruletable ;
// when drawing, these are used
liferender *renderer ;
viewport *view ;
int uviewh, uvieww, viewh, vieww, mag, pmag, kadd ;
int oddgen ;
int bmleft, bmtop, bmlev, shbmsize, logshbmsize ;
int quickb, deltaforward ;
int llbits, llsize ;
char *llxb, *llyb ;
liferules qliferules ;
"""
