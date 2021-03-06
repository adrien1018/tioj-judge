#ifndef UTILS_H_
#define UTILS_H_

// This header defines helper functions for simplicity

#include <string>
#include <vector>
#include <stdexcept>
#include <filesystem>

#ifdef DEBUG
#include <iostream>
#define _DEBUG1(x) std::cerr << x << std::endl;
#define _DEBUG2(x, y) std::cerr << x << ": " << y << std::endl;
#else
#define _DEBUG1(x)
#define _DEBUG2(x, y)
#endif

void ThrowErrno();
// Path checking & manipulating
bool IsValidFilename(const std::string&);
// contains no ..
bool IsDownwardPath(const std::filesystem::path&);

// C++-style printf-like string format
template <class T> T _Convert(const T& obj) { return obj; }
// inline is necessary
inline const char* _Convert(const std::string& obj) { return obj.c_str(); }

template <class... T>
std::string FormatStr(const std::string& str, T... args) {
  char* strp;
  if (asprintf(&strp, str.c_str(), _Convert(args)...) == -1) {
    throw std::runtime_error("asprintf failed");
  }
  std::string res(strp);
  free(strp);
  return res;
}

// Basic rule for MySQL database, table and column name
bool IsValidDBName(const std::string&);

// Convert raw timestamp value to string
std::string DateTimeStr(long long);

// Convert string to raw timestamp value
long long DateTimeVal(const std::string&);

// split a comma-separated string into array of strings
std::vector<std::string> SplitString(const std::string&);

// merge a list into a string
template <class Iterator, class Func>
inline std::string MergeString(Iterator first, Iterator last, Func tostr) {
  std::string res, strtemp;
  size_t pos;
  for (; first != last; first++) {
    strtemp = tostr(*first);
    if (strtemp.find('\"') != std::string::npos ||
        strtemp.find(',')  != std::string::npos ||
        strtemp.find('\n') != std::string::npos ||
        strtemp.find('\r') != std::string::npos) {
      res += '\"';
      pos = 0;
      while ((pos = strtemp.find('\"', pos)) != std::string::npos) {
        strtemp.insert(pos, 1, '\"');
        pos += 2;
      }
      res += strtemp;
      res += '\"';
    }
    else res += strtemp;
    res += ',';
  }
  if (res.size()) res.pop_back();
  return res;
}
// helper functions for ease of use
template <class Iterator>
inline std::string MergeString(Iterator first, Iterator last) {
  return MergeString(first, last, [](const std::string& str){ return str; });
}
template <class T, class Func>
inline std::string MergeString(const T& cont, Func tostr) {
  return MergeString(cont.begin(), cont.end(), tostr);
}
inline std::string MergeString(const std::vector<std::string>& vec) {
  return MergeString(vec.begin(), vec.end());
}
// caution: only use when both sides are in csv format
//  (a string with no ',' and '\"' is in valid format, like numbers)
inline std::string MergeString(const std::string& a, const std::string& b) {
  if (a.empty()) return b;
  if (b.empty()) return a;
  return a + ',' + b;
}

#endif
