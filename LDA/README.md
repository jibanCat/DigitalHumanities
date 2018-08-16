# An experimental implementation of LDA in Classical Chinese Text

As a scientist, I am quite interested in how parameters estimation works in a text data. It turns out there is a standard way to achieve parameter estimation in the text: Latent Dirichlet allocation (or LDA, in short). The LDA paper can be found in [here](http://jmlr.csail.mit.edu/papers/v3/blei03a.html), which is written by David M. Blei, Andrew Y. Ng, and Michael I. Jordan.

As any other probabilistic graphical model (PGM), LDA treated a bunch of documents as a generative process. The assumption here is that a document can be represented as a bag-of-words.

![PGM of LDA in wiki](https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Latent_Dirichlet_allocation.svg/500px-Latent_Dirichlet_allocation.svg.png)(PGM of LDA in wiki)

Since there is no standard sentence segmentation method in classical Chinese, I would like to approach this problem carefully -- using n-grams. And, through features extracted from n-grams, to define several topics of features (bag-of-words).

## Resources

- LDA implementation in [`Stan`](http://mc-stan.org/): [lda.stan](https://github.com/stan-dev/example-models/blob/master/misc/cluster/lda/lda.stan)
- LDA implementation in [`PyMC3`](https://docs.pymc.io/) : [lda-advi-aevb](http://docs.pymc.io/notebooks/lda-advi-aevb.html)
- A talk of Topic Modelling (speaker: David Blei) : [video](https://www.youtube.com/watch?v=FkckgwMHP2s)