#include <ctime>
#include <iotream>

int main() {
std::time_t t2 = std::time(nullptr);
cout << std::put_time(std::localtime(&t), "%Y-%m-%d %H.%M.%S") << "." << msecs << endl;
}


   1
   2 #ifndef SRC_COMMON_MUTEX_H_
   3 #define SRC_COMMON_MUTEX_H_
   4
   5 #include <assert.h>
   6 #include <errno.h>
   7
   8 #include <pthread.h>
   9
  10 #include <string.h>
  11 #include <stdexcept>
  12 #include <string>
  13 #include <stdlib.h>
  14
  15 #include "common/check_error.h"
  16 #include "common/scoped_locker.h"
  17 #include "glog/logging.h"
  18
  19
  20 // namespace common {
  21
  22 class ConditionVariable;
  23
  24 class MutexBase
  25 {
  26 protected:
  27     // type converter, force enable errorcheck in debug mode
  28     static int DebugEnabled(int type)
  29     {
  30         if (type == PTHREAD_MUTEX_RECURSIVE)
  31             return type;
  32 #ifdef NDEBUG
  33         return type;
  34 #else
  35         // alwasy enable errcheck in debug mode
  36         return PTHREAD_MUTEX_ERRORCHECK_NP;
  37 #endif
  38     }
  39     explicit MutexBase(int type)
  40     {
  41         pthread_mutexattr_t attr;
  42         CHECK_PTHREAD_ERROR(pthread_mutexattr_init(&attr));
 43         CHECK_PTHREAD_ERROR(pthread_mutexattr_settype(&attr, type));
  44         CHECK_PTHREAD_ERROR(pthread_mutex_init(&m_mutex, &attr));
  45         CHECK_PTHREAD_ERROR(pthread_mutexattr_destroy(&attr));
  46     }
  47
  48     ~MutexBase()
  49     {
  50         CHECK_PTHREAD_ERROR(pthread_mutex_destroy(&m_mutex));
  51         // Since pthread_mutex_destroy will set __data.__kind to -1 and check
  52         // it in pthread_mutex_lock/pthread_mutex_unlock, nothing is necessary
  53         // to do for destructed access check.
  54     }
  55 public:
  56     void Lock()
  57     {
  58         CHECK_PTHREAD_ERROR(pthread_mutex_lock(&m_mutex));
  59         assert(IsLocked());
  60     }
  61
  62     bool TryLock()
  63     {
  64         int ret = pthread_mutex_trylock(&m_mutex);
  65         if (ret == 0) {
  66             return true;
  67         }
  68         if (ret == EBUSY || ret == EAGAIN) {
  69             return false;
  70         }
  71         LOG(ERROR) << "mutex trylock failed";
  72         abort();
  73         return false;
  74     }
  75
  76     // for test and debug only
  77     bool IsLocked() const
  78     {
  79         // by inspect internal data
  80         return m_mutex.__data.__lock > 0;
  81     }
  82
  83     void Unlock()
  84     {
  85         assert(IsLocked());
  86         CHECK_PTHREAD_ERROR(pthread_mutex_unlock(&m_mutex));
  87         // NOTE: can't check unlocked here, maybe already locked by other thread
  88     }
  89 private:
  90     MutexBase(const MutexBase& right);
  91     MutexBase& operator = (const MutexBase& right);
  92
  93 private:
  94     pthread_mutex_t m_mutex;
  95     friend class ConditionVariable;
  96 };
  97
  98 /// simple mutex, fast but nonrecursive
  99 /// if same thread try to acquire the lock twice, deadlock would occur.
 100 class SimpleMutex : public MutexBase
 101 {
 102 public:
 103     typedef ScopedLocker<SimpleMutex> Locker;
 104     SimpleMutex() : MutexBase(DebugEnabled(PTHREAD_MUTEX_DEFAULT))
 105     {
 106     }
 107 };
 108
 109 /// RecursiveMutex can be acquired by same thread multiple times, but slower than
 110 /// SimpleMutex
 111 class RecursiveMutex : public MutexBase
 112 {
 113 public:
 114     typedef ScopedLocker<RecursiveMutex> Locker;
 115     RecursiveMutex() : MutexBase(PTHREAD_MUTEX_RECURSIVE)
 116     {
 117     }
 118 };
 119
 120 /// try to spin some time if can't acquire lock, if still can't acquire, wait.
 121 class AdaptiveMutex : public MutexBase
 122 {
 123 public:
 124     typedef ScopedLocker<AdaptiveMutex> Locker;
 125     AdaptiveMutex() : MutexBase(DebugEnabled(PTHREAD_MUTEX_ADAPTIVE_NP))
 126     {
127     }
 128 };
 129
 130 class Mutex : public MutexBase
 131 {
 132 public:
 133     typedef ScopedLocker<MutexBase> Locker;
 134     Mutex() : MutexBase(PTHREAD_MUTEX_ERRORCHECK_NP)
 135     {
 136     }
 137     template <typename T>
 138     explicit Mutex(const T& src) : MutexBase(PTHREAD_MUTEX_ERRORCHECK_NP)
 139     {
 140     }
 141 };
 142
 143 class FairMutex : public MutexBase {
 144  public:
 145   typedef ScopedLocker<MutexBase> Locker;
 146   FairMutex() : MutexBase(PTHREAD_MUTEX_TIMED_NP) {
 147   }
 148
 149 };
 150
 151 typedef ScopedLocker<MutexBase> MutexLocker;
 152
 153 // check ing missing variable name, eg MutexLocker(m_lock);
 154 #define MutexLocker(x) STATIC_ASSERT(false, "Mising variable name of MutexLocker")
 155
 156 /// null mutex for template mutex param placeholder
 157 /// NOTE: don't make this class uncopyable
 158 class NullMutex
 159 {
 160 public:
 161     typedef ScopedLocker<NullMutex> Locker;
 162 public:
 163     NullMutex() : m_locked(false)
 164     {
 165     }
 166
 167     void Lock()
 168     {
 169         m_locked = true;
 170     }
 171
 172     bool TryLock()
 173     {
 174         m_locked = true;
 175         return true;
 176     }
 177
 178     // by inspect internal data
 179     bool IsLocked() const
 180     {
 181         return m_locked;
 182     }
 183
 184     void Unlock()
 185     {
 186         m_locked = false;
 187     }
 188 private:
 189     bool m_locked;
 190 };
 191
 192 // } // namespace common
 193
 194 #endif // SRC_COMMON_MUTEX_H_
 195

