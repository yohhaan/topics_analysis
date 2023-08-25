# Topics Analysis: Privacy and Utility Goals

This repository contains the source code used in our privacy and utility
analysis of the Topics API for the Web from the [Privacy
Sandbox](https://privacysandbox.com/).


## Topics API for the Web

With the Topics API for the Web, Google aims to replace third-party cookies for
personalized advertising. Find more details about our analysis in our paper
[Interest-disclosing Mechanisms for Advertising are Privacy-*Exposing* (not
Preserving)](https://arxiv.org/abs/2306.03825):

```bibtex
@inproceedings{topicsweb23_beugin,
      title={Interest-disclosing Mechanisms for Advertising are Privacy-Exposing (not Preserving)},
      author={Yohan Beugin and Patrick McDaniel},
      booktitle={Proceedings on {Privacy} {Enhancing} {Technologies} {Symposium} ({PETS})},
      year={2024},
      month={july},
}
```

---
## Getting Started

1. Clone this [topics_analysis](https://github.com/yohhaan/topics_analysis)
   repository and the
   [sandbox_dependencies](https://github.com/yohhaan/sandbox_dependencies)
   submodule at once with:
   - `git clone --recurse-submodules git@github.com:yohhaan/topics_analysis.git` (SSH)
   - `git clone --recurse-submodules
     https://github.com/yohhaan/topics_analysis.git` (HTTPS)

A `Dockerfile` is provided under `.devcontainer/` (for direct integration with
[VS Code](https://gist.github.com/yohhaan/b492e165b77a84d9f8299038d21ae2c9)). To
manually build the image and deploy the Docker container, follow the
instructions below:

**Requirement:** [Docker](https://www.docker.com/products/docker-desktop)

2. Build the Docker image:
```sh
docker build -t topics_analysis .devcontainer/
```

3. Deploy a Docker container:
```sh
docker run --rm -it -v ${PWD}:/workspaces/topics_analysis \
    -w /workspaces/topics_analysis \
    --entrypoint bash topics_analysis:latest
```

**Note:** some commands to reproduce our results may take a long time to execute
depending on the amount of resources of your machine. We recommend running the
above command to deploy a Docker container in a
[`screen`](https://www.gnu.org/software/screen/) session that you can then
detach and attach to your terminal as needed.

4. Fetch the required Privacy Sandbox dependencies:
```
cd sandbox_dependencies
./fetch_all.sh
cd ..
```
## Reproduction Steps

Refer to the instructions provided in
[petsymposium-artifact2024.1/template.md](petsymposium-artifact2024.1/template.md)
to reproduce our analysis of the Topics API for the Web.