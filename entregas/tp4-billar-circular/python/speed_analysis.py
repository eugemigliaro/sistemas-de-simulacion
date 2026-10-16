"""Rapidez: histogramas completos y mínimos cuadrados con un parámetro térmico."""
import numpy as np


def histogram(values, edges):
    values, edges = np.asarray(values), np.asarray(edges)
    if (values.size == 0 or not np.isfinite(values).all() or np.any(values < 0)
            or edges[0] != 0 or np.any(np.diff(edges) <= 0)
            or values.max() > edges[-1]):
        raise ValueError("Muestra vacia, invalida o fuera de los bins")
    return np.histogram(values, bins=edges)[0] / (values.size * np.diff(edges))


def mb_bins(edges, mass, theta):
    """Densidad media teórica en cada bin; no se renormaliza el rango finito."""
    if mass <= 0 or theta <= 0:
        raise ValueError("Masa y energia termica deben ser positivas")
    survival = np.exp(-mass * np.asarray(edges)**2 / (2 * theta))
    return -np.diff(survival) / np.diff(edges)


def fit_theta(density, edges, mass, reference):
    """Minimiza sum (histograma - modelo integrado/bin)^2, sin pesos libres."""
    density = np.asarray(density)
    if (reference <= 0 or mass <= 0 or density.shape != (len(edges)-1,)
            or not np.isfinite(density).all() or np.any(density < 0)):
        raise ValueError("Datos de ajuste invalidos")

    def objective(log_theta):
        return float(np.sum((density - mb_bins(edges, mass, np.exp(log_theta)))**2))

    grid = np.linspace(np.log(reference/100), np.log(reference*100), 401)
    errors = np.array([objective(x) for x in grid])
    i = int(np.argmin(errors))
    if i in (0,len(grid)-1):
        raise ValueError("Minimo fuera del rango de busqueda")
    a,b = grid[i-1],grid[i+1]
    ratio = (np.sqrt(5)-1)/2
    x,y = b-ratio*(b-a), a+ratio*(b-a)
    fx,fy = objective(x),objective(y)
    for _ in range(80):
        if fx < fy:
            b,y,fy = y,x,fx
            x=b-ratio*(b-a); fx=objective(x)
        else:
            a,x,fx = x,y,fy
            y=a+ratio*(b-a); fy=objective(y)
    theta = float(np.exp((a+b)/2))
    return theta, objective(np.log(theta))


def stationary_suffix(densities, thetas, edges, tv_limit, theta_limit, minimum=3):
    """Primer sufijo con >=minimum comparaciones adyacentes estables.

    Criterio descriptivo predefinido; no es una prueba de equilibrio ni determina
    el primer instante físico de relajación.
    """
    densities, thetas = np.asarray(densities), np.asarray(thetas)
    tv = .5*np.sum(np.abs(np.diff(densities,axis=0))*np.diff(edges),axis=1)
    relative = np.abs(np.diff(thetas))/thetas[:-1]
    passes = (tv <= tv_limit) & (relative <= theta_limit)
    for start in range(len(passes)-minimum+1):
        if np.all(passes[start:]):
            return start, tv, relative
    return None, tv, relative
