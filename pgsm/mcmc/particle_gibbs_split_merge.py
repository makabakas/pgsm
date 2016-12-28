from __future__ import division

import numpy as np

from pgsm.math_utils import exp_normalize
from pgsm.particle_utils import get_cluster_labels
from pgsm.utils import setup_split_merge, relabel_clustering


class ParticleGibbsSplitMerge(object):

    def __init__(self, kernel, pgs, num_anchors=None):
        self.kernel = kernel
        self.pgs = pgs

        self.num_anchors = num_anchors

    def sample(self, clustering, data, num_iters=1000):
        for _ in range(num_iters):
            anchors, sigma = self._setup_split_merge(clustering)
            self.kernel.setup(anchors, clustering, data, sigma)
            particles = self.pgs.sample(data[sigma], self.kernel)
            sampled_particle = self._sample_particle(particles)
            self._get_updated_clustering(clustering, sampled_particle, sigma)
        return clustering

    def _get_updated_clustering(self, clustering, particle, sigma):
        restricted_clustering = get_cluster_labels(particle)
        max_idx = clustering.max()
        clustering[sigma] = restricted_clustering + max_idx + 1
        return relabel_clustering(clustering)

    def _sample_particle(self, particles):
        probs, _ = exp_normalize([float(x.log_W) for x in particles])
        particle_idx = np.random.multinomial(1, probs).argmax()
        return particles[particle_idx]

    def _setup_split_merge(self, clustering):
        if self.num_anchors is None:
            num_anchors = np.random.poisson(0.8) + 2
        else:
            num_anchors = self.num_anchors
        return setup_split_merge(clustering, num_anchors)
