#include <Python.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>
#include <stdio.h>

#define CONSECUTIVE_CHAR_PENALTY (7)
#define BOUNDARY_PENALTY (5)
#define SUB_WORD_PENALTY (3)
#define WORD_PENALTY (1)

#define SKIPED_SUBWORD_WORD_PENALTY (3)
#define SKIPED_WORD_PENALTY (5)


struct input {
  const char *pattern;
  size_t pattern_len;
  const char *string;
  size_t string_len;
  bool first;
  bool debug;
};

enum position_kind {
  MIDDLE,
  BOUNDARY,
  SUB_WORD_START,
  WORD_START
};

static const char *position_str[] = {"MIDDLE", "BOUNDARY", "SUB_WORD_START",
                                     "WORD_START"};

static const int skipped_penalty[] = {0, 0, SKIPED_SUBWORD_WORD_PENALTY,
                                      SKIPED_WORD_PENALTY};
static const int char_penalty[] = {0, BOUNDARY_PENALTY, SUB_WORD_PENALTY,
                                   WORD_PENALTY};

static enum position_kind classify_possition(const struct input *input, size_t i)
{
  if (i == 0)
    return WORD_START;
  const char curr = input->string[i];
  const char prev = input->string[i-1];
  const bool prev_digit = isdigit(prev);
  const bool prev_alpha = isalpha(prev);

  if (isalpha(curr)) {
    const bool after_subword_sep = (prev_digit || prev == '-' || prev == '_');

    if (!prev_alpha && !after_subword_sep)
      return WORD_START;
    if (after_subword_sep || (isupper(curr) && islower(prev)))
      return SUB_WORD_START;
    return MIDDLE;
  }
  if ((isdigit(curr) && !prev_digit) || ispunct(curr))
    return BOUNDARY;
  return MIDDLE;
}

static int min(int x, int y)
{
  return x < y ? x : y;
}

#define DEBUG(fmt, ...)                                                        \
  do {                                                                         \
    if (input->debug)                                                          \
      fprintf(stderr, fmt "\n", ##__VA_ARGS__);                                \
  } while (0)

#define DEBUG_INDENT(fmt, ...)                                                 \
  DEBUG("%*s[p%03zu] " fmt, (int)pattern_offset, "", pattern_offset,           \
        ##__VA_ARGS__)

static int helper(const struct input *input, size_t pattern_offset,
           size_t string_offset) {
  int best = INT_MAX;
  enum position_kind skipped_position = MIDDLE;

  if (pattern_offset == input->pattern_len)
  {
    DEBUG_INDENT("End of pattern and string");
    return 0;
  }
  if (string_offset == input->string_len)
  {
    DEBUG_INDENT("End of string but not pattern");
    return INT_MAX;
  }
  DEBUG_INDENT("matching '%s' in '%s' (pattern_offset=%zu string_offset=%zu)",
        input->pattern + pattern_offset, input->string + string_offset,
        pattern_offset, string_offset);

  for (size_t i = string_offset; i < input->string_len; ++i) {
    /* TODO: check case */
    int char_matches = tolower(input->pattern[pattern_offset]) == tolower(*(input->string + i));
    enum position_kind position = classify_possition(input, i);
    int penalty = 0;

    /* check for skipped */
    if (!char_matches) {
      if (pattern_offset != 0 && position > skipped_position) {
        if (skipped_penalty[position] > 0)
          DEBUG_INDENT("skipped position %s (penalty %d)",
                       position_str[position], skipped_penalty[position]);
        skipped_position = position;
      }
      continue;
    }

    /* recursive */
    if (position >= BOUNDARY) {
      DEBUG_INDENT("%s char i=%zu (penalty %d)", position_str[position], i,
                   char_penalty[position]);
      penalty = char_penalty[position];
      if (skipped_position >= position)
        penalty += skipped_penalty[skipped_position];
    } else if (i == string_offset) {
      DEBUG_INDENT("Consecutive char i=%zu (penalty %d)", i, CONSECUTIVE_CHAR_PENALTY);
      penalty = CONSECUTIVE_CHAR_PENALTY;
    } else {
      continue;
    }

    int score = helper(input, pattern_offset + 1, i + 1);
    if (score == INT_MAX)
      continue;
    if (input->first)
      return score;
    score += penalty;
    best = min(best, score);
    DEBUG_INDENT("score: %d, best: %d", score, best);
  }

  DEBUG_INDENT("return best score %d", best);
  return best;
}

int rank(const char *pattern, const char *string, int first, int debug) {
  struct input input_struct = {.pattern = pattern,
                               .pattern_len = strlen(pattern),
                               .string = string,
                               .string_len = strlen(string),
                               .first = first,
                               .debug = debug};
  const struct input *input = &input_struct;
  DEBUG("========================================================================");
  DEBUG("match pattern '%s' against string '%s'", pattern, string);

  int score = helper(input, 0, 0);
  return (score == INT_MAX) ? -1 : score;
}

static PyObject *py_rank(PyObject *self, PyObject *args) {
  const char *pattern;
  const char *string;
  int first;
  int debug;

  if (!PyArg_ParseTuple(args, "sspp", &pattern, &string, &first, &debug))
    return NULL;
  return PyLong_FromLong(rank(pattern, string, first, debug));
}


static PyMethodDef module_methods[] = {
    {"rank", py_rank, METH_VARARGS, "Rank."},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT, "abbrev_matcher", /* name of module */
    NULL,                          /* module documentation, may be NULL */
    -1, /* size of per-interpreter state of the module,
           or -1 if the module keeps state in global variables. */
    module_methods};

PyMODINIT_FUNC PyInit_abbrev_matcher_c(void) { return PyModule_Create(&module); }
