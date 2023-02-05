import sys

def life_fatal(s: str) -> None:
    return
def life_warning(s: str) -> None:
    return
def life_status(s: str) -> None:
    return
def life_begin_progress(dlgtitle: str) -> None:
    return
def life_abort_progress(fracdone: float, newmsg: str) -> bool:
    return False
def life_get_user_rules() -> str:
    return ""
def life_get_rules_dir() -> str:
    return ""
def is_aborted() -> bool:
    return False
def get_debug_file() -> file:
    return


class LifeErrors:
    """To substitute your own routines, use the following class."""
    def fatal(s: str) -> None:
        return

    def warning(s: str) -> None:
        return

    def status(s: str) -> None:
        return

    def begin_progress(dlgtitle: str) -> None:
        return

    def abort_progress(fracdone: float, newmsg: str) -> bool:
        return False

    virtual bool (double , const char *newmsg) = 0 ;
    virtual void endprogress() = 0 ;
    virtual const char *getuserrules() = 0 ;
    virtual const char *getrulesdir() = 0 ;
    static void seterrorhandler(lifeerrors *obj) ;
    bool aborted ;
