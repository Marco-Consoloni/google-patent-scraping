# Dataset for Multimodal Information Retrieval - Googl Patent Scraping

This repository provides scripts for constructing an evaluation dataset for multimodal information retrieval (IR). The pipeline enables the automatic creation of the dataset by scraping front-page images and first claims from Google Patents (https://patents.google.com/).

We use existing patent citation metadata to establish query–document relationships: for each citing patent, its cited patents are retrieved and used as relevant documents. This approach allows the automatic generation of relevance labels, eliminating the need for costly and time-consuming manual annotation (see Fig. 1). 


![readme_img](assets/citations_by_examiner.png)

**Fig. 1** - *query-document reslationships using*

The query–document relationships derived from patent citation metadata are used as ground-truth relevance labels to evaluate retrieval performance. Specifically, these relationships enable the computation of standard information retrieval metrics, including Precision@k, Recall@k, and F1-score@k, by comparing the set of k documents retrieved by a model for a given query against the corresponding set of cited patents assumed to be relevant.

The resulting evaluation dataset was used in the following published work: *"Consoloni, M., Giordano, V., Galatolo, F. A., Cimino, M. G. C. A., & Fantoni, G. (2025). Uncovering the limits of visual-language models in engineering knowledge representation. Proceedings of the Design Society, 5, 3261-3270. https://doi.org/10.1017/pds.2025.10340"*

