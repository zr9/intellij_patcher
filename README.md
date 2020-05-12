# Intellij idea patcher

Patcher providing ability to modify a few things in *idea* which is not available through plugins or other way(except source code modification). Available patches is explained below.

## Legal notice

This project was made for study and fun purposes only. If you plan to use it for any other product than **Intellij CE**, use it at your own risk, since it clearly violates any **Intellij** product license except **CE**.

## Usage

Clone, copy your `platform-impl.jar` to `res` dir and execute `./patch.py`.
You can find `platform-impl.jar` in your intellij install dir inside `lib` dir.

## Docker

To deploy *patcher* using a pre-built `Dockerfile`, follow the instructions in [docker repo](https://github.com/zr9/intellij_patcher_docker).

## Supported versions

![intellij 2019.2](https://badgen.net/badge/intellij/2019.2/blue)
![intellij 2020.1](https://badgen.net/badge/intellij/2020.1/blue)

## Supported versions (reported by Users)

![phpstorm 2019.2](https://badgen.net/badge/phpstorm/2019.2/blue)
![phpstorm 2019.3](https://badgen.net/badge/phpstorm/2019.3/blue)
![phpstorm 2020.1](https://badgen.net/badge/phpstorm/2020.1/blue)

## Patches explanation & examples

All explanations and examples [are here](./examples/examples.md)