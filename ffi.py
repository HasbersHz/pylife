from cffi import FFI


ffi = FFI()

ffi.cdef("""
struct brick { /* 64 bytes */
   unsigned int d[16] ;
} ;
struct tile { /* 32 bytes */
   struct brick *b[4] ;
   short c[6] ;
   int flags, localdeltaforward ;
} ;
struct supertile { /* 44 bytes */
   struct supertile *d[8] ;
   int flags ;
   int pop[2] ;
} ;
""")

test = ffi.new("struct brick*")
print(test)
