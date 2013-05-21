import re

TASK_PATTERNS = [
  r'let\s+(me|us)\s+know\s+(if|when|what).+(\?|\.)',
  r'look\s+into\s+this',
  r'(could|can|will)\s+you\s+(please)?.+\?',
  r'(is it|would it be)\s+possible.*\?',
  r'please\s+advi(c|s)e',
  r'would(\s+\w*)appreciate\s+(if|when|what)',
  r'(could|can|will)\s+you\s+(please)?.+(update)?\?',
  r'please\s+take\s+a\s+look',
  r'(do|did|have)\s+(we|you).+\?',
  r'(i\s+was|we\s+were)\s+wondering.+\?',
  r'is\s+this\s+something.+\?',
  r'(i|we)\s+(will)?\s+need\s+your'
]

URGENT_PATTERNS = [
  r'asap|urgently|respond urgently|this is urgent'
]

def check_if_task(text):
  for pattern in TASK_PATTERNS:
    if re.search(pattern, text, flags=re.IGNORECASE) is not None:
      return True
  return False

def check_if_urgent(text):
  for pattern in URGENT_PATTERNS:
    if re.search(pattern, text, flags=re.IGNORECASE) is not None:
      return True
  return False