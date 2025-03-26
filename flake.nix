{
  description = "TEA flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python311;
        tea = pkgs.python311Packages.buildPythonPackage rec {
          pname = "TEA";
          version = "2025.2.1";
          src = ./.;
          format = "pyproject";

          propagatedBuildInputs = with pkgs.python311Packages; [ transformers setuptools ];

          meta = {
            description = "Taxonomic Entity Augmentation";
            license = pkgs.lib.licenses.mit;
            maintainers = with pkgs.lib.maintainers; [ ];
          };
        };
      in {
        packages.default = tea;

        devShells.default = pkgs.mkShell {
          buildInputs = [ python tea ];
          shellHook = ''
            export HF_HOME="$HOME/.cache/huggingface"
          '';
        };
      });
}