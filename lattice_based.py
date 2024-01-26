import numpy as np
import sympy as sp
import random
import math

# print readable values
np.set_printoptions(suppress=True)

# different random errors for seed = -1, same random errors for seed > -1
seed = -1

if seed >= 0:
    random.seed(seed)


# check if columnvectors in basis are linear independent
def linear_independence(matrix):
    _, inds = sp.Matrix(matrix).rref()
    if len(inds) == np.shape(matrix)[0]:
        return 1
    else:
        return 0


class GHH:
    # B = "good" lattice basis as private key
    # n = dimension of the lattice
    # H = "bad" lattice basis as public key using the Hermite Normal Form of the private key
    def __init__(self, B):
        self.__B = B
        self.__n = self.__B.shape[0]
        self.__H = self.HNF()[0]

    def get_public(self):
        return self.__H

    # extended euclidian algorithm
    def gcd_ext(self, r0: int, r1: int) -> tuple:
        if r0 < 0:
            vz0 = -1
            r0 = -r0
        else:
            vz0 = 1
        if r1 < 0:
            vz1 = -1
            r1 = -r1
        else:
            vz1 = 1

        x0, x1, y0, y1 = 1, 0, 0, 1

        while True:
            if r1 == 0:
                return r0, vz0 * x0, vz1 * y0
            q = r0 // r1
            r0, r1 = r1, r0 % r1
            x0, x1 = x1, x0 - x1 * q
            y0, y1 = y1, y0 - y1 * q

    # lower triangular basis using Nemhauser/Wolsey algorithm
    def HNF(self):
        # perform Nemhauser/Wolsey algorithm as described here (https://kola.opus.hbz-nrw.de/frontdoor/deliver/index/docId/211/file/Studienarbeit_Kerstin_Susewind.pdf) on page 34.
        H = self.__B
        n = self.__n
        U = np.identity(n)
        i = 0
        while True:
            # Step 1
            j = i + 1
            while j <= n - 1:
                # Step 2
                if H[i, j] != 0:
                    r, p, q = self.gcd_ext(H[i, i], H[i, j])
                    temp = np.identity(n)
                    temp[i, i] = p
                    temp[j, i] = q
                    temp[i, j] = -H[i, j] / r
                    temp[j, j] = H[i, i] / r
                    H = H.dot(temp)
                    U = U.dot(temp)
                j = j + 1
            # Step 3
            if H[i, i] < 0:
                temp = np.identity(n)
                temp[i, i] = -1
                H = H.dot(temp)
                U = U.dot(temp)
            j = 0
            while True:
                # Step 4
                if j == i:
                    if i == n - 1:
                        return (H, U)
                    else:
                        i = i + 1
                        break
                temp = np.identity(n)
                temp[i, j] = -math.ceil(H[i, j] / H[i, i])
                H = H.dot(temp)
                U = U.dot(temp)
                if j == i - 1:
                    i = i + 1
                    if i > n - 1:
                        return (H, U)
                    else:
                        break
                if j < i - 1:
                    j = j + 1

    def encrypt(self, x, pk):
        # map message to latticepoint
        m = pk.dot(x)

        # generate random noise vector with magnitude 2
        e = np.array([random.uniform(-1, 1) for _ in range(self.__n)])
        e *= 2 / np.linalg.norm(e)

        # encrypt by adding noise vector to lattice point
        c = m + e

        return c

    def decrypt(self, c):
        # multiply with inverted B
        B_inv_c = np.linalg.inv(self.__B).dot(c)

        # round values to closest integer
        B_inv_c_rounded = B_inv_c.round()

        # multiply with B to recover m
        recovered_m = self.__B.dot(B_inv_c_rounded)

        # solve for H to recover x
        recovered_x = np.linalg.inv(self.__H).dot(recovered_m)

        return recovered_x

    def decrypt_with_H(self, c):
        # multiply with inverted B
        H_inv_c = np.linalg.inv(self.__H).dot(c)

        # round values to closest integer
        H_inv_c_rounded = H_inv_c.round()

        # multiply with B to recover m
        recovered_m = self.__H.dot(H_inv_c_rounded)

        # solve for H to recover x
        recovered_x = np.linalg.inv(self.__H).dot(recovered_m)

        return recovered_x


# since this one is hard-coded, you have to edit it here if you want to try another one
# it has to be quadratic and the columnvectors should be linear independent
base = np.array([[4, -2, 1, 0],
                 [0, -1, 5, 2],
                 [-1, 6, 1, -1],
                 [0, 1, -1, 6]])

if linear_independence(base) == 0:
    print("The columnvectors of the basis B are not linear independent.")
else:
    X = GHH(base)

    message = np.array([3, 5, 7, 9])

    print(f"Public key:")
    print(X.get_public())
    print()

    print(f"Message: {message}")
    print()

    encrypted_message = X.encrypt(message, X.get_public())

    print(f"Encrypted message: {encrypted_message}")
    print()

    recovered_message = X.decrypt(encrypted_message)

    print(f"Recovered message: {recovered_message}")
    print()

    recovered_message_public = X.decrypt_with_H(encrypted_message)

    print(
        f"Recovered message using public key instead of private key: {recovered_message_public}")
    print()
