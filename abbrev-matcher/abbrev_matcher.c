#include <Python.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>
#include <stdio.h>

#define CHAR_PENALTY (1)
#define SKIPED_WORD_PENALTY (5)
#define WORD_START_PENALTY (3)


struct input {
  const char *pattern;
  size_t pattern_len;
  const char *string;
  size_t string_len;
};

static bool check_word_start(char prev, char curr)
{
  return (isupper(curr) && !isupper(prev)) ||
         (isalpha(curr) && !isalpha(prev)) ||
         (isdigit(curr) && !isdigit(prev)) ||
         (ispunct(curr) && curr != '-' && curr != '-');
}

static int helper(const struct input *input, size_t pattern_offset,
           size_t string_offset) {
  int best = INT_MAX;
  int skipped_words = 0;

  if (pattern_offset == input->pattern_len)
    return 0;
  if (string_offset == input->string_len)
    return INT_MAX;
  /* fprintf(stderr, "matching '%s' in '%s' (pattern_offset=%zu string_offset=%zu)\n",  input->pattern + pattern_offset, input->string + string_offset, */
  /*         pattern_offset, string_offset); */

  for (size_t i = string_offset; i < input->string_len; ++i) {
    int char_matches = tolower(input->pattern[pattern_offset]) == tolower(*(input->string + i));
    int word_start =
        i == 0 || check_word_start(input->string[i - 1], input->string[i]);
    /* fprintf(stderr, "i=%zu char_matches=%d word_start=%d\n", i, char_matches, word_start); */
    if (i == string_offset) {
      if (!char_matches)
        continue;
      best = helper(input, pattern_offset + 1, string_offset + 1);
    }
    if (!word_start)
      continue;
    if (!char_matches) {
      if (pattern_offset != 0)
        ++skipped_words;
      continue;
    }
    int sub_score = helper(input, pattern_offset + 1, i + 1);
    if (sub_score == INT_MAX)
      continue;
    int new =
        skipped_words * SKIPED_WORD_PENALTY + WORD_START_PENALTY + sub_score;
    if (new < best)
      best = new;
  }
  /* fprintf(stderr, "'%s' in '%s' -> %d\n", input->pattern + pattern_offset, input->string + string_offset, best); */
  return (best == INT_MAX) ? INT_MAX : (best + CHAR_PENALTY);
}



int match(const char *pattern, const char *string) {
  struct input input = {.pattern = pattern,
                        .pattern_len = strlen(pattern),
                        .string = string,
                        .string_len = strlen(string)};
  int score = helper(&input, 0, 0);
  if (score == INT_MAX)
    return -1;
  return score;
}

static PyObject *py_match(PyObject *self, PyObject *args) {
  const char *pattern;
  const char *string;

  if (!PyArg_ParseTuple(args, "ss", &pattern, &string))
    return NULL;
  int res = match(pattern, string);
  return PyLong_FromLong(res);
}

static PyMethodDef module_methods[] = {
    {"match", py_match, METH_VARARGS, "Match."},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT, "spam", /* name of module */
    NULL,                          /* module documentation, may be NULL */
    -1, /* size of per-interpreter state of the module,
           or -1 if the module keeps state in global variables. */
    module_methods};

PyMODINIT_FUNC PyInit_abbrev_matcher_c(void) { return PyModule_Create(&module); }
