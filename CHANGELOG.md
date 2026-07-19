# Changelog

## [2.1.1](https://github.com/MaturityBuilder/gitlab-compliance/compare/v2.1.0...v2.1.1) (2026-07-19)


### Bug Fixes

* restore github actions ci docs ([#86](https://github.com/MaturityBuilder/gitlab-compliance/issues/86)) ([8399298](https://github.com/MaturityBuilder/gitlab-compliance/commit/8399298fb2bc3bfc7ee61831f5e08a35d9133fcd))

## [2.1.0](https://github.com/MaturityBuilder/gitlab-compliance/compare/v2.0.1...v2.1.0) (2026-07-18)


### Features

* add include-depth limits, policy autofix, and MR create/comment ([ecca69a](https://github.com/MaturityBuilder/gitlab-compliance/commit/ecca69a1eae1cd76d488bdeb917650a550988fe0))
* docs quality, BDD outlines, builtin policies, and test coverage ([#29](https://github.com/MaturityBuilder/gitlab-compliance/issues/29)) ([1d326e7](https://github.com/MaturityBuilder/gitlab-compliance/commit/1d326e7800840fc0ac776d8674124e2a9dbae852))
* gitstrings decorate your gitlab ci yml to produce documentation ([ae3a29c](https://github.com/MaturityBuilder/gitlab-compliance/commit/ae3a29cedefc832d789a676b9a3071d1e7430702))
* setup ossf scorecard health check ([#53](https://github.com/MaturityBuilder/gitlab-compliance/issues/53)) ([ba10aea](https://github.com/MaturityBuilder/gitlab-compliance/commit/ba10aea9b32c90bcc7f8db54daf1025eccd8b029))


### Bug Fixes

* align dependabot multi-ecosystem config ([#68](https://github.com/MaturityBuilder/gitlab-compliance/issues/68)) ([c07cb92](https://github.com/MaturityBuilder/gitlab-compliance/commit/c07cb92156b607f987a1d12f37feb536eecd4f7c))
* exclude changelog from markdownlint ([#62](https://github.com/MaturityBuilder/gitlab-compliance/issues/62)) ([5417ef7](https://github.com/MaturityBuilder/gitlab-compliance/commit/5417ef790ae0dcb0473338f258222ea8157e2572))
* fix mkdocs site name ([#65](https://github.com/MaturityBuilder/gitlab-compliance/issues/65)) ([318cfa4](https://github.com/MaturityBuilder/gitlab-compliance/commit/318cfa4459f58b9080567efba68e7ed7b21c5465))
* **get-attributes:** format list/dict attribute values for the table ([#35](https://github.com/MaturityBuilder/gitlab-compliance/issues/35)) ([98d99e3](https://github.com/MaturityBuilder/gitlab-compliance/commit/98d99e38e6d210c5bc4bde6c257c1691e87d7a72))
* pre-commit job ([#64](https://github.com/MaturityBuilder/gitlab-compliance/issues/64)) ([06086e6](https://github.com/MaturityBuilder/gitlab-compliance/commit/06086e6817520b87b665a217e96874753dc54961))
* SBOM Job Setup ([#58](https://github.com/MaturityBuilder/gitlab-compliance/issues/58)) ([fdb0a86](https://github.com/MaturityBuilder/gitlab-compliance/commit/fdb0a86e128f86b04a9c130bf6444caf9c8ac435))
* sbom sha pinning ([2da1684](https://github.com/MaturityBuilder/gitlab-compliance/commit/2da16843600c47599627e8ad702f95e12563c126))
* sbom sha pinning ([#55](https://github.com/MaturityBuilder/gitlab-compliance/issues/55)) ([6a351f3](https://github.com/MaturityBuilder/gitlab-compliance/commit/6a351f370d6174c04ff8987260c381ef2f651dec))
* scorecard job permissions ([#57](https://github.com/MaturityBuilder/gitlab-compliance/issues/57)) ([6ffdb1c](https://github.com/MaturityBuilder/gitlab-compliance/commit/6ffdb1cd47340eb6fb9f0a859db592969f710361))
* scorecard permissions ([f81a931](https://github.com/MaturityBuilder/gitlab-compliance/commit/f81a9319f39a3f2b4aa8adcdcffbd906ecc71e39))
* stop zensical builds on pr ([a483a7b](https://github.com/MaturityBuilder/gitlab-compliance/commit/a483a7b4f4f65b433081b21120a7084f461c31a1))


### Dependencies

* **deps:** bump the all-dependencies group with 8 updates ([#69](https://github.com/MaturityBuilder/gitlab-compliance/issues/69)) ([e9e2840](https://github.com/MaturityBuilder/gitlab-compliance/commit/e9e284095950acdd6fcd649fad81f3c7d2ee5a21))
* **deps:** bump the major group across 1 directory with 2 updates ([#50](https://github.com/MaturityBuilder/gitlab-compliance/issues/50)) ([a58baed](https://github.com/MaturityBuilder/gitlab-compliance/commit/a58baed569c631fa52ea149261dde280bad64b23))


### Documentation

* add AGENTS.md with Cursor Cloud setup instructions ([#39](https://github.com/MaturityBuilder/gitlab-compliance/issues/39)) ([72329cf](https://github.com/MaturityBuilder/gitlab-compliance/commit/72329cf76838c5a9f765bdfc861635c9eaf84041))
* improve documentation ([b3427e6](https://github.com/MaturityBuilder/gitlab-compliance/commit/b3427e6390e22252157b90372cdb4f69f4048fc8))
* improve documentation ([bfa1a89](https://github.com/MaturityBuilder/gitlab-compliance/commit/bfa1a892b81a78611eca7da0bfa754e966282fb5))
* update documentation and include gifs of command usage ([#73](https://github.com/MaturityBuilder/gitlab-compliance/issues/73)) ([3f65b72](https://github.com/MaturityBuilder/gitlab-compliance/commit/3f65b729bbeae0a7b778a9df29261f323a0ad7dc))

## [2.0.1](https://github.com/MaturityBuilder/gitlab-compliance/compare/v2.0.0...v2.0.1) (2026-07-08)

### Bug Fixes (2.0.1)

* disable container scanning uploads to security tab
  ([#27](https://github.com/MaturityBuilder/gitlab-compliance/issues/27))
  ([c562f6b](<https://github.com/MaturityBuilder/gitlab-compliance/commit/c562f6b>
  fae04a822127c6c9c5541a3567d3a85b3))
* python version pinning
  ([3fccebc](<https://github.com/MaturityBuilder/gitlab-compliance/commit/3fccebc>
  1988153ad8c07cddb10d6f8bcce350b8a))
* python version pinning
  ([1ca3157](<https://github.com/MaturityBuilder/gitlab-compliance/commit/1ca3157>
  1d1acb388f0849bbde76a32110d0ad347))

## [2.0.0](https://github.com/MaturityBuilder/gitlab-compliance/compare/v1.0.6...v2.0.0) (2026-07-07)

### BREAKING CHANGES (2.0.0)

* moved gitlab documentation creation to `generate` command

### Features (2.0.0)

* add automated versioning
  ([651d267](<https://github.com/MaturityBuilder/gitlab-compliance/commit/651d267>
  862b006f05e158a59ae8dcbe3a37cbd0b))
* add automated versioning
  ([8cbe6fc](<https://github.com/MaturityBuilder/gitlab-compliance/commit/8cbe6fc>
  eef6009729a26c90342c4af5f56742ab3))
* add automated versioning
  ([87e323e](<https://github.com/MaturityBuilder/gitlab-compliance/commit/87e323e>
  65e43e3a67569a472518a2f1b56d79f9e))
* add click cli framework
  ([0da3ef3](<https://github.com/MaturityBuilder/gitlab-compliance/commit/0da3ef3>
  97c949ee1c99cc39505ce6bb69124e83e))
* add click cli framework
  ([d28a082](<https://github.com/MaturityBuilder/gitlab-compliance/commit/d28a082>
  d1a345936cc03ee892197d43251969c6e))
* add click cli framework
  ([5aa02fd](<https://github.com/MaturityBuilder/gitlab-compliance/commit/5aa02fd>
  30f2ca4b4a596a8c3af501efb04c2fc10))
* add click cli framework
  ([c2cc7c1](<https://github.com/MaturityBuilder/gitlab-compliance/commit/c2cc7c1>
  5f5af9d92f7e6d10ff4c8410559fdee2a))
* add click cli framework
  ([3af5bdb](<https://github.com/MaturityBuilder/gitlab-compliance/commit/3af5bdb>
  2385f29eb9d88d2047cf92872c40363e1))
* add click cli framework
  ([99cdeb9](<https://github.com/MaturityBuilder/gitlab-compliance/commit/99cdeb9>
  c0c28548209ac6d25c8956b4f8f7ad0d0))
* add click cli framework
  ([68f3afb](<https://github.com/MaturityBuilder/gitlab-compliance/commit/68f3afb>
  e94a92be5a31b5643873e8cb5a247aa56))
* add click cli framework
  ([97f4041](<https://github.com/MaturityBuilder/gitlab-compliance/commit/97f4041>
  b2dfb887da1f23719632d6ae8aab0f974))
* add click cli framework
  ([c9d45ba](<https://github.com/MaturityBuilder/gitlab-compliance/commit/c9d45ba>
  21fb52a65af752748a0c9be6a24be9ed9))
* add docker hub and pypi support
  ([d88f301](<https://github.com/MaturityBuilder/gitlab-compliance/commit/d88f301>
  61be8cae6535058934a2bb390341e050e))
* add docker hub and pypi support
  ([8e74ab6](<https://github.com/MaturityBuilder/gitlab-compliance/commit/8e74ab6>
  b9c795ee70e739ab195d5bfe4230ac9a2))
* add docker hub and pypi support
  ([2873434](<https://github.com/MaturityBuilder/gitlab-compliance/commit/2873434>
  a8bc2c03ed01d6324127ca6306fbd870e))
* add docker hub and pypi support
  ([f539c27](<https://github.com/MaturityBuilder/gitlab-compliance/commit/f539c27>
  36eab4685a692a03c10ee63de68d24520))
* add docker hub and pypi support
  ([b8fbea9](<https://github.com/MaturityBuilder/gitlab-compliance/commit/b8fbea9>
  8ca3e89f55ff8600e4dee1f1aeffe1ff0))
* add docker hub and pypi support
  ([e7c58a0](<https://github.com/MaturityBuilder/gitlab-compliance/commit/e7c58a0>
  80cb1367910aa91d770aea94aacbc1b36))
* add module to support workflow
  ([fcaf454](<https://github.com/MaturityBuilder/gitlab-compliance/commit/fcaf454>
  3f79b95265e80e3e69a7568ba938e26c3))
* add pre-commit hooks
  ([d09c7b1](<https://github.com/MaturityBuilder/gitlab-compliance/commit/d09c7b1>
  2f0f9e8c3f2e3f548ef99936e589c46e6))
* add precommit hook
  ([bd8aa92](<https://github.com/MaturityBuilder/gitlab-compliance/commit/bd8aa92>
  b5b39f35fb05ebc7e579edd8de79b4723))
* add support for inputs
  ([8130325](<https://github.com/MaturityBuilder/gitlab-compliance/commit/8130325>
  c69cc4779c07b9250640aeb87d52a96e6))
* add unit tests
  ([94dca26](<https://github.com/MaturityBuilder/gitlab-compliance/commit/94dca26>
  2461f4d1a0d431bc6ff43ecfd3e5555d0))
* Adds get-attribute command
  ([46496ad](<https://github.com/MaturityBuilder/gitlab-compliance/commit/46496ad>
  5fcb5e3f06b659f242017713a19153d58))
* adds support for additional gitlab-docs commands
  ([46496ad](<https://github.com/MaturityBuilder/gitlab-compliance/commit/46496ad>
  5fcb5e3f06b659f242017713a19153d58))
* clean up project structure
  ([30908d7](<https://github.com/MaturityBuilder/gitlab-compliance/commit/30908d7>
  1ac0d96d3ef8fd2ed4771efa5018c3889))
* code for variables and jobs
  ([e47a435](<https://github.com/MaturityBuilder/gitlab-compliance/commit/e47a435>
  d83e984690bb4ad06d2646c4c14e60e21))
* gitlab-docs
  ([bb2a64e](<https://github.com/MaturityBuilder/gitlab-compliance/commit/bb2a64e>
  4ec7601c767fdaafea3cc2da939606cf8))
* gitlab-docs
  ([537509a](<https://github.com/MaturityBuilder/gitlab-compliance/commit/537509a>
  ce78c67dda82a9985593016827cc66dc0))
* gldocs includes code
  ([cc4bddf](<https://github.com/MaturityBuilder/gitlab-compliance/commit/cc4bddf>
  28c9285134caa3e4b6e60a004d0030bb9))
* gldocs includes code
  ([3de28e2](<https://github.com/MaturityBuilder/gitlab-compliance/commit/3de28e2>
  091d2b93912aa9add545ac832b63384b3))
* improve documentation
  ([e8c8068](<https://github.com/MaturityBuilder/gitlab-compliance/commit/e8c8068>
  ee8a925c2169b6af0118f8cec55f504d0))
* improve documentation
  ([00c3ebe](<https://github.com/MaturityBuilder/gitlab-compliance/commit/00c3ebe>
  f32e3ddd7973e55fed8124ed423a5bb55))
* improve documentation
  ([35a9db5](<https://github.com/MaturityBuilder/gitlab-compliance/commit/35a9db5>
  798fdbf0662bccca0d0e5b57e9fb5403b))
* improve documentation
  ([75c741c](<https://github.com/MaturityBuilder/gitlab-compliance/commit/75c741c>
  27cdde68f47fb75bc71a828ec523d12a4))
* improve documentation
  ([421aa50](<https://github.com/MaturityBuilder/gitlab-compliance/commit/421aa50>
  192e6f714e1ee6d80c61b199447329936))
* improve documentation
  ([bd7088e](<https://github.com/MaturityBuilder/gitlab-compliance/commit/bd7088e>
  b461ea8369b7c800552b676e0afbbfdf4))
* improve error handling
  ([b4e918c](<https://github.com/MaturityBuilder/gitlab-compliance/commit/b4e918c>
  688ce551daa2648a826c72fd40e77ba49))
* improve error handling
  ([2062926](<https://github.com/MaturityBuilder/gitlab-compliance/commit/2062926>
  c02c0bb049612135d1bcc18538049d97f))
* improve error handling
  ([81be2ab](<https://github.com/MaturityBuilder/gitlab-compliance/commit/81be2ab>
  9384af65c0b614312e5622c70d36d27af))
* improve error handling
  ([070d3fb](<https://github.com/MaturityBuilder/gitlab-compliance/commit/070d3fb>
  b66eeff798a342719141d788f93ed081c))
* improve security posture by using prebuilt hardened docker images.
  ([b22e680](<https://github.com/MaturityBuilder/gitlab-compliance/commit/b22e680>
  3a97b969948b705b6174bb32492f83ff6))
* improve the mkdoc github pages and setup docker
  ([#22](https://github.com/MaturityBuilder/gitlab-compliance/issues/22))
  ([fa0f4ff](<https://github.com/MaturityBuilder/gitlab-compliance/commit/fa0f4ff>
  d204c1b8ef6b31620b36cad5baaebd6cb))
* includes synatax
  ([cc1710f](<https://github.com/MaturityBuilder/gitlab-compliance/commit/cc1710f>
  b1cd77d72c369e4d7976d3b6888eee168))
* initial gitlab-docs
  ([b32a9fc](<https://github.com/MaturityBuilder/gitlab-compliance/commit/b32a9fc>
  37729771c84cd7ded262a4a735e2aaa49))
* publish gitlab-compliance and gitlab-docs CLI entry points
  ([#11](https://github.com/MaturityBuilder/gitlab-compliance/issues/11))
  ([a34c129](<https://github.com/MaturityBuilder/gitlab-compliance/commit/a34c129>
  3e6a566207d09266883976b0708918a14))
* setup oidc auth to pypi
  ([21457c4](<https://github.com/MaturityBuilder/gitlab-compliance/commit/21457c4>
  b55b09b98d121dce094d6f4c6937961bb))
* setup oidc auth to pypi
  ([bd4fb58](<https://github.com/MaturityBuilder/gitlab-compliance/commit/bd4fb58>
  06c32bdbe424a05811c8849a944e40204))
* setup oidc auth to pypi
  ([579bf4f](<https://github.com/MaturityBuilder/gitlab-compliance/commit/579bf4f>
  f7ad67f3723dd19bf30d11544594b29ea))
* setup oidc auth to pypi
  ([a13c23c](<https://github.com/MaturityBuilder/gitlab-compliance/commit/a13c23c>
  45a2b83db8806ca94b608aad166a39f8a))
* setup oidc auth to pypi
  ([f97b884](<https://github.com/MaturityBuilder/gitlab-compliance/commit/f97b884>
  c979782f2c3aa13ab00e0f3eb4af3a72c))
* setup oidc auth to pypi
  ([32f6224](<https://github.com/MaturityBuilder/gitlab-compliance/commit/32f6224>
  177bd247cd8b1e5d968fb157f5551592b))
* setup oidc auth to pypi
  ([8c5c5bb](<https://github.com/MaturityBuilder/gitlab-compliance/commit/8c5c5bb>
  48e1326bcca99d97cbf60f9f65afbb124))
* setup oidc auth to pypi
  ([f9e89d2](<https://github.com/MaturityBuilder/gitlab-compliance/commit/f9e89d2>
  ad0ac454c020ff2af0d3220da7013eb67))
* setup oidc auth to pypi
  ([305243d](<https://github.com/MaturityBuilder/gitlab-compliance/commit/305243d>
  0195d9e386575351a71a7bf38e9349097))
* setup oidc auth to pypi
  ([d48dc82](<https://github.com/MaturityBuilder/gitlab-compliance/commit/d48dc82>
  33fbd8043a07bf6e4683fe1f88e8926ad))
* setup oidc auth to pypi
  ([a956f27](<https://github.com/MaturityBuilder/gitlab-compliance/commit/a956f27>
  181c42f882f6013cbed8b690229619e22))
* setup oidc auth to pypi
  ([f0d560d](<https://github.com/MaturityBuilder/gitlab-compliance/commit/f0d560d>
  f026924ba19d0c6fea5e701f5edce8814))
* setup oidc auth to pypi
  ([8c81384](<https://github.com/MaturityBuilder/gitlab-compliance/commit/8c81384>
  05109798201c90efdc05532d4179962ee))
* setup oidc auth to pypi
  ([bf0819c](<https://github.com/MaturityBuilder/gitlab-compliance/commit/bf0819c>
  217cf9774e5fb7dba7521448bd51969ae))
* setup oidc auth to pypi
  ([3bc3833](<https://github.com/MaturityBuilder/gitlab-compliance/commit/3bc3833>
  9d4e7366098d6a1a795f589fd4520e9d4))
* setup oidc auth to pypi
  ([14d07de](<https://github.com/MaturityBuilder/gitlab-compliance/commit/14d07de>
  feb12ab3660b343e4dc84778c2e77cdf6))
* setup oidc auth to pypi
  ([53a177c](<https://github.com/MaturityBuilder/gitlab-compliance/commit/53a177c>
  d94325d8d140eefe2fb5c61e5ac28e8ee))
* setup oidc auth to pypi
  ([cd6cf10](<https://github.com/MaturityBuilder/gitlab-compliance/commit/cd6cf10>
  6a2416cb4d0972c36c5feddc9fbe3b791))
* supports multi document yml files
  ([41ea811](<https://github.com/MaturityBuilder/gitlab-compliance/commit/41ea811>
  02008f2ac46abc0975fba3b4a86cdee09))

### Bug Fixes (2.0.0)

* .gitlab-ci.yml publish job
  ([92643eb](<https://github.com/MaturityBuilder/gitlab-compliance/commit/92643eb>
  f1a758dc4cdc706232fc32dfbfae3f743))
* add release please workflow
  ([409bb79](<https://github.com/MaturityBuilder/gitlab-compliance/commit/409bb79>
  11ace2b13f5d88f9bd0ac4c8879b58f41))
* build
  ([1d59b77](<https://github.com/MaturityBuilder/gitlab-compliance/commit/1d59b77>
  d6774d8731dc57f80c5d1136a300e08a3))
* build
  ([5b9a90b](<https://github.com/MaturityBuilder/gitlab-compliance/commit/5b9a90b>
  595b9e567e09f2b23c9a58f7afc8ad718))
* error handling when parsing job
  ([b170ac9](<https://github.com/MaturityBuilder/gitlab-compliance/commit/b170ac9>
  e821f2161f0ac608f454d48375d93391b))
* get attributes output
  ([a03a622](<https://github.com/MaturityBuilder/gitlab-compliance/commit/a03a622>
  ae6567ba45d3cb6ce5ca6150784a4cf0e))
* gitlab ci workflow rule
  ([f445257](<https://github.com/MaturityBuilder/gitlab-compliance/commit/f445257>
  5197f0b98443aeb732b0fb3bb791c2d76))
* gitlab default image pinning to python:3.12.11
  ([d1eb59e](<https://github.com/MaturityBuilder/gitlab-compliance/commit/d1eb59e>
  db4efb73703c7b0f1de8220b347fac52f))
* job output format
  ([73d0d0d](<https://github.com/MaturityBuilder/gitlab-compliance/commit/73d0d0d>
  549d6860c0a9dec074b6c2c9d42dc514f))
* link styling
  ([d9aa956](<https://github.com/MaturityBuilder/gitlab-compliance/commit/d9aa956>
  0c4892e6b13f3e9eab59d7b9fdd12cac5))
* linter errors
  ([51ff1ab](<https://github.com/MaturityBuilder/gitlab-compliance/commit/51ff1ab>
  d46e5f118593d0fd290257ae59819781d))
* optimise pipeline using smaller images
  ([8b4120b](<https://github.com/MaturityBuilder/gitlab-compliance/commit/8b4120b>
  078d2775f270d0457e942ab97a12b8f79))
* publish and version bump dep.
  ([de590ab](<https://github.com/MaturityBuilder/gitlab-compliance/commit/de590ab>
  29c2936afbce7ac1159cef6b8b0d1e8a7))
* pyproject missing version property
  ([9516434](<https://github.com/MaturityBuilder/gitlab-compliance/commit/9516434>
  857e8240693cffc101bd02deb0c448ad6))
* pyproject missing version property
  ([4e1c931](<https://github.com/MaturityBuilder/gitlab-compliance/commit/4e1c931>
  a8755f942ad4540d3aeb99c563b7db336))
* pyproject missing version property
  ([f6c1ee2](<https://github.com/MaturityBuilder/gitlab-compliance/commit/f6c1ee2>
  7a566074d175c202c06eb1a9919178de6))
* release pipeline
  ([3e5e73b](<https://github.com/MaturityBuilder/gitlab-compliance/commit/3e5e73b>
  492ed9d6790ca63a32c28430f79dd4c1b))
* remove dry_mode param from get-attribute command
  ([297da13](<https://github.com/MaturityBuilder/gitlab-compliance/commit/297da13>
  909e7138cae687e7ad1988d55623f8728))
* runner tags
  ([a01e564](<https://github.com/MaturityBuilder/gitlab-compliance/commit/a01e564>
  538884764997c26c5213c2821ae19a183))
* stop publish running on main branch
  ([8b57c98](<https://github.com/MaturityBuilder/gitlab-compliance/commit/8b57c98>
  28091dca33278b1bf7dcfbabbe6d6e15f))
* tag pipleine
  ([533c104](<https://github.com/MaturityBuilder/gitlab-compliance/commit/533c104>
  c19eeeb8daffc48a46d28989c67de6dd8))
* tag pipleine
  ([3eb2a03](<https://github.com/MaturityBuilder/gitlab-compliance/commit/3eb2a03>
  74a631e34a68ac17bad05227342fab183))
* tag pipleine
  ([7383052](<https://github.com/MaturityBuilder/gitlab-compliance/commit/7383052>
  2f2051f0585a82ab7ac27cdca1ccc8314))
* tag pipleine
  ([8f47e44](<https://github.com/MaturityBuilder/gitlab-compliance/commit/8f47e44>
  692d2f43e276a7acabb1fc7cf6ed46dfa))
* unit tests
  ([2a1f49e](<https://github.com/MaturityBuilder/gitlab-compliance/commit/2a1f49e>
  d77152af48a474b677a7f892570c2d89b))
* variable error handling
  ([ae5ac6e](<https://github.com/MaturityBuilder/gitlab-compliance/commit/ae5ac6e>
  71f575b80113da9a2e515a43fcf5d4a54))
* version bumping in pyproject
  ([76665fa](<https://github.com/MaturityBuilder/gitlab-compliance/commit/76665fa>
  ac8af4254d95bdb1bd010da321bd69d6e))
* version bumping in pyproject
  ([47964e3](<https://github.com/MaturityBuilder/gitlab-compliance/commit/47964e3>
  d9e15ecb7035f8efc27ba47cacbe5d976))
* version bumping in pyproject
  ([006a032](<https://github.com/MaturityBuilder/gitlab-compliance/commit/006a032>
  7c27628dd217ea560d0ad519e3f577b17))
* version bumping in pyproject
  ([613cb0a](<https://github.com/MaturityBuilder/gitlab-compliance/commit/613cb0a>
  9e337cd2e0834d67b8df5370c04fb5d81))
* version bumping in pyproject
  ([cc1ac69](<https://github.com/MaturityBuilder/gitlab-compliance/commit/cc1ac69>
  5a1801fb3dc6340389499c076a8338859))
* version bumping in pyproject
  ([01e7d29](<https://github.com/MaturityBuilder/gitlab-compliance/commit/01e7d29>
  6dfe50a62dc5900302e352f014088ac5d))
* version bumping in pyproject
  ([c5214ea](<https://github.com/MaturityBuilder/gitlab-compliance/commit/c5214ea>
  842e465327a93ddaf63d2f5da38b290eb))
* version bumping in pyproject
  ([75a7577](<https://github.com/MaturityBuilder/gitlab-compliance/commit/75a7577>
  f795ce9568139cbf44bc8a717572c42e6))
* version bumping in pyproject
  ([fb14b45](<https://github.com/MaturityBuilder/gitlab-compliance/commit/fb14b45>
  2e85901442a9b6b6b9976e721e9a7c5f2))
* version bumping in pyproject
  ([7166b37](<https://github.com/MaturityBuilder/gitlab-compliance/commit/7166b37>
  3fb88d9b92e74d359f449ce59a4c1483e))
* version bumping in pyproject
  ([cce10ef](<https://github.com/MaturityBuilder/gitlab-compliance/commit/cce10ef>
  28f43c6859e4bdf7244bb08ae4691c9e4))
* version bumping in pyproject
  ([f54b750](<https://github.com/MaturityBuilder/gitlab-compliance/commit/f54b750>
  9facf7b8f7e0ac7fea281d47ba879e79d))
* version bumping in pyproject
  ([7d1b684](<https://github.com/MaturityBuilder/gitlab-compliance/commit/7d1b684>
  c2c4d2278f712c50f02307d1cb1b26c4f))
* version bumping in pyproject
  ([35a6d3b](<https://github.com/MaturityBuilder/gitlab-compliance/commit/35a6d3b>
  c122cc03ea7db9c5d2a7cc6983dbaac06))
* version bumping in pyproject
  ([45bbceb](<https://github.com/MaturityBuilder/gitlab-compliance/commit/45bbceb>
  4a28c3a7bed08c8d7113a5bcc3bb14fb6))
* version bumping in pyproject
  ([6be717d](<https://github.com/MaturityBuilder/gitlab-compliance/commit/6be717d>
  68508650c0515c0198a0cf096e7221017))
* version bumping in pyproject
  ([5cc4342](<https://github.com/MaturityBuilder/gitlab-compliance/commit/5cc4342>
  1d709f39be8b6fa5b03df68c3c6238822))
* version bumping in pyproject
  ([2dcfba4](<https://github.com/MaturityBuilder/gitlab-compliance/commit/2dcfba4>
  5a67eda3075c8caa15cdd4f27b3d2e668))
* version bumping in pyproject
  ([62a5f7a](<https://github.com/MaturityBuilder/gitlab-compliance/commit/62a5f7a>
  3f84b58cf4f857c55c3db68b4e84dc5d0))
* version bumping in pyproject
  ([b2253c3](<https://github.com/MaturityBuilder/gitlab-compliance/commit/b2253c3>
  4373894c436cc2a8aa7c3d007d4ff0c0b))
* version bumping in pyproject
  ([9f5cbb7](<https://github.com/MaturityBuilder/gitlab-compliance/commit/9f5cbb7>
  eae1dd76abc095c440d0ec39295798892))
* version bumping in pyproject
  ([419b50f](<https://github.com/MaturityBuilder/gitlab-compliance/commit/419b50f>
  977916eabab1767620ea1faa8a6e64c5a))
* version bumping in pyproject
  ([0f150d2](<https://github.com/MaturityBuilder/gitlab-compliance/commit/0f150d2>
  8c93f25be4d0888ae6503e2b5d12cfa6c))
* workflow properly and error handling
  ([73632a6](<https://github.com/MaturityBuilder/gitlab-compliance/commit/73632a6>
  2e52f4fa67b3d3048c6555f8016d38a41))
* workflow properly and error handling
  ([30970f7](<https://github.com/MaturityBuilder/gitlab-compliance/commit/30970f7>
  cd107bfd7baacccc3f9c612ec888648c2))
* workflow properly and error handling
  ([ef8bd48](<https://github.com/MaturityBuilder/gitlab-compliance/commit/ef8bd48>
  1c832e85da9e1e46df2d760872d009a4d))

### Documentation

* Improves documentation
  ([46496ad](<https://github.com/MaturityBuilder/gitlab-compliance/commit/46496ad>
  5fcb5e3f06b659f242017713a19153d58))
* MkDocs Material build and publish for GitLab Pages and GitHub Pages
  ([#20](https://github.com/MaturityBuilder/gitlab-compliance/issues/20))
  ([5360dd6](<https://github.com/MaturityBuilder/gitlab-compliance/commit/5360dd6>
  9b00e026e4bd585188af79aabc90e8248))
* MkDocs Material site, review builds, and refreshed guide
  ([#21](https://github.com/MaturityBuilder/gitlab-compliance/issues/21))
  ([e286707](<https://github.com/MaturityBuilder/gitlab-compliance/commit/e286707>
  20111944dda426d2104750341d7e67590))
