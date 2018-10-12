# Slight modification from
# https://gist.github.com/markuskowa/20700860c09af1ca4cc828f8dc2e36b3

with builtins;

let
   pkgs = import <nixpkgs> { overlays = []; };

   # clean evals
   cc1 = pkgs.lib.mapAttrs (n: v: (builtins.tryEval v).value ) pkgs;
   # Only top level derivations
   cc2 = pkgs.lib.filterAttrs (n: v: pkgs.lib.isDerivation v) cc1;
   # Filter for meta tags
   cc3 = pkgs.lib.filterAttrs (n: v: v ? "meta") cc2;

   hasMetaCondition = condition: attribute: (with pkgs.lib; concatStringsSep "\n"
        (
          mapAttrsToList (name: v: "${v.meta.position}") (
          filterAttrs (n: v: (if condition then (hasAttr attribute v.meta) else (! hasAttr attribute v.meta)) && (hasAttr "position" v.meta) ) cc3
          )
          ));

  checkCommand = condition: attribute: (
    pkgs.runCommand "check-meta-${attribute}"
     {}
     ''
       mkdir $out
       cat << EOF > $out/unsorted
       ${hasMetaCondition condition attribute}
       EOF
       cat $out/unsorted  | sort | uniq > $out/unique
     ''
  );
in {
  maintainer = checkCommand false "maintainers";
  license = checkCommand false "license";
  broken = checkCommand true "broken";
  homepage = checkCommand false "homepage";
}
