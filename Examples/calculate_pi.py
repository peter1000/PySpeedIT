""" Example: calculate_pi.py
"""


def recip_square(i_):
   return 1.0 / (i_ ** 2)


# need to supply a n_ in the `speed_it modules__func_tuples`
# noinspection PyUnusedLocal
def approx_pi(n_=100000):
   val = 0.
   for k_ in range(1, n_ + 1):
      val += recip_square(k_)
   to_be_returned = (6 * val) ** 0.5
