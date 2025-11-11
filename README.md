# Topics Analysis: Privacy and Utility Goals
[![DOI](https://zenodo.org/badge/650219863.svg)](https://doi.org/10.5281/zenodo.17583710)

This repository contains the source code used in our privacy and utility analysis of the Topics API for the Web from the [Privacy Sandbox](https://privacysandbox.com/).

## Topics API for the Web

With the Topics API for the Web, Google aims to replace third-party cookies for personalized advertising. Find more details about our analysis in our paper [Interest-disclosing Mechanisms for Advertising are Privacy-*Exposing* (not Preserving)](https://doi.org/10.56553/popets-2024-0004):

```bibtex
@inproceedings{topicsweb24_beugin,
      title={Interest-disclosing Mechanisms for Advertising are Privacy-Exposing (not Preserving)},
      author={Yohan Beugin and Patrick McDaniel},
      booktitle={Proceedings on {Privacy} {Enhancing} {Technologies} {Symposium} ({PETS})},
      year={2024},
      month={july},
      doi={10.56553/popets-2024-0004}
}
```

---
## Getting Started

**Requirement:** [Docker Engine](https://docs.docker.com/engine/install/)

- Clone this [topics_analysis](https://github.com/yohhaan/topics_analysis) repository and the [sandbox_dependencies](https://github.com/yohhaan/sandbox_dependencies) submodule at once with:
   - `git clone --recurse-submodules git@github.com:yohhaan/topics_analysis.git` (SSH)
   - `git clone --recurse-submodules https://github.com/yohhaan/topics_analysis.git` (HTTPS)

- Note: the [`.devcontainer/`](.devcontainer/) directory contains the config for integration with VS Code (see [guide here](https://github.com/PoPETS-AEC/examples-and-other-resources/blob/main/resources/vs-code-docker-integration.md)).

- Then, follow either set of instructions (or install dependencies manually):

> <details><summary>Using the Docker image from the Container Registry</summary>
>
> This [GitHub workflow](.github/workflows/build-push-docker-image.yaml)
> automatically builds and pushes the Docker image to GitHub's Container Registry
> when the `Dockerfile` or the `requirements.txt` files are modified.
>
> 1. Pull the Docker image:
> ```bash
> docker pull ghcr.io/yohhaan/topics_analysis:main
> ```
> 2. Launch the Docker container, attach the current working directory (i.e.,
> run from the root of the cloned git repository) as a volume, set the context
> to be that volume, and provide an interactive bash terminal:
> ```bash
> docker run --rm -it -v ${PWD}:/workspaces/topics_analysis \
>     -w /workspaces/topics_analysis \
>     --entrypoint bash ghcr.io/yohhaan/topics_analysis:main
> ```
> </details>


> <details><summary>Using a locally built Docker image</summary>
>
> 1. Build the Docker image:
> ```bash
> docker build -t topics_analysis:main .
> ```
> 2. Launch the Docker container, attach the current working directory (i.e.,
> run from the root of the cloned git repository) as a volume, set the context
> to be that volume, and provide an interactive bash terminal:
> ```bash
> docker run --rm -it -v ${PWD}:/workspaces/topics_analysis \
>     -w /workspaces/topics_analysis \
>     --entrypoint bash topics_analysis:main
> ```
> </details>

**Note:** some commands to reproduce our results may take a long time to execute depending on the amount of resources of your machine. We recommend running the above command to deploy a Docker container in a [`screen`](https://www.gnu.org/software/screen/) session that you can then detach and attach to your terminal as needed.

- Fetch the required Privacy Sandbox dependencies:
```
cd sandbox_dependencies
./fetch_all.sh
cd ..
```
## Reproduction Steps

Refer to the instructions provided in [petsymposium-artifact2024.1/template.md](petsymposium-artifact2024.1/template.md) to reproduce our analysis of the Topics API for the Web.
