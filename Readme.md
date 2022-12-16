[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<br />
<p align="center">
  <h3 align="center">BSVTools</h3>

  <p align="center">
    Useful helpers for Bluespec developers.
    <br />
    <a href="https://github.com/esa-tu-darmstadt/BSVTools/wiki"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/esa-tu-darmstadt/BSVTools/issues">Report Bug</a>
    ·
    <a href="https://github.com/esa-tu-darmstadt/BSVTools/issues">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)



<!-- ABOUT THE PROJECT -->
## About The Project

This project provides helper scripts that can be used to create Bluespec projects. The generated Makefile supports
  - Compile and simulate using Bluesim
  - Compile and simulate using `bsc` supported Verilog simulators
  - Build IP-XACT Packets for use in Xilinx Vivado

### Built With

* Python 3
* Bluespec Compiler [`bsc`](https://github.com/B-Lang-org/bsc)


## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

Have the bluespec compiler and Python 3 installed.

### Installation

1. Clone the repo
```bash
git clone https://github.com/esa-tu-darmstadt/BSVTools.git
```
2. Create a new directory for the Bluespec project
3. Run the following command to create all necessary files for the Bluespec project. The `--test_dir` is for big projects where it is better to separate testbench from source code.
```bash
path/to/BSVTools/bsvNew.py PROJECT_NAME [--test_dir]
```
4. (Optional) Add libraries to the created library directory (e.g. [BlueAXI](https://github.com/esa-tu-darmstadt/BlueAXI) or [BlueLib](https://github.com/esa-tu-darmstadt/BlueLib))

The script creates a number of basic Bluespec modules that can be extended as desired.

#### On a second machine

BSVTools stores device specific information in the file `.bsv_tools`. By default this file is excluded from Git using `.gitignore`. A new `.bsv_tools` file can be created using:

```bash
path/to/BSVTools/bsvAdd.py
```

## Usage

Simulate using Bluesim

```bash
make
```

Simulate using Verilog (Modelsim/Questasim by default)

```bash
make SIM_TYPE=VERILOG
```

Build IP-XACT packet (Needs Vivado in path):

```sh
make SIM_TYPE=VERILOG ip
```

_For more examples, please refer to the [Documentation](https://github.com/esa-tu-darmstadt/BSVTools/wiki)_



<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/esa-tu-darmstadt/BSVTools/issues) for a list of proposed features (and known issues).



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

Embedded Systems and Applications Group - https://www.esa.informatik.tu-darmstadt.de

Project Link: [https://github.com/esa-tu-darmstadt/BSVTools](https://github.com/esa-tu-darmstadt/BSVTools)


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[issues-shield]: https://img.shields.io/github/issues/esa-tu-darmstadt/BSVTools.svg?style=flat-square
[issues-url]: https://github.com/esa-tu-darmstadt/BSVTools/issues
[license-shield]: https://img.shields.io/github/license/esa-tu-darmstadt/BSVTools.svg?style=flat-square
[license-url]: https://github.com/esa-tu-darmstadt/BSVTools/blob/master/LICENSE
