from cffi import FFI


ffi = FFI()

ffi.cdef("""
struct brick { /* 64 bytes */
   unsigned int d[16] ;
} ;
struct tile { /* 56 bytes */
   struct brick *b[4] ;
   short c[6] ;
   int flags, localdeltaforward ;
} ;
struct supertile { /* 80 bytes */
   struct supertile *d[8] ;
   int flags ;
   int pop[2] ;
} ;
""")

test = ffi.new("struct supertile*")
print(test)
