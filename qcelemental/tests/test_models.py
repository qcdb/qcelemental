from qcelemental.models import Molecule

mol = {
  "name": "butuane",
  "identifiers": {
    "inchikey": "IJDNQMDRQITEOD-UHFFFAOYSA-N",
    "standard_inchi": "InChI=1S/C4H10/c1-3-4-2/h3-4H2,1-2H3",
    "canonical_explicit_hydrogen_smiles": "[H]C([H])([H])C([H])([H])C([H])([H])C([H])([H])[H]",
    "canonical_isomeric_explicit_hydrogen_mapped_smiles": "[H:5][C:1]([H:6])([H:7])[C:3]([H:11])([H:12])[C:4]([H:13])([H:14])[C:2]([H:8])([H:9])[H:10]",
    "canonical_isomeric_explicit_hydrogen_smiles": "[H]C([H])([H])C([H])([H])C([H])([H])C([H])([H])[H]",
    "canonical_isomeric_smiles": "CCCC",
    "canonical_smiles": "CCCC"
  },
  "molecular_charge": 0,
  "molecular_multiplicity": 1,
  "symbols": ["C", "C", "C", "C", "H", "H", "H", "H", "H", "H", "H", "H", "H", "H"],
  "geometry": [0.764938, -1.379087,  1.33855 ,
               4.803756,  3.062888,  5.516074,
               3.093872, -0.344024,  2.664593,
               2.486877,  2.056899,  4.147074,
               0.035351,  0.022213,  0.044298,
               1.224314, -3.078871,  0.252992,
               0.687522, -1.875996,  2.724953,
               5.568104,  1.648263,  6.817593,
               4.312974,  4.746522,  6.612934,
               6.29054 ,  3.581917,  4.174546,
               3.847091, -1.789514,  3.943152,
               4.559751,  0.050644,  1.254844,
               1.770032,  3.515675,  2.862177,
               0.993691,  1.671622,  5.530409],
  "provenance": {},
  "connectivity": [[0, 2, 1], [0, 4, 1], [0, 5, 1], [0, 6, 1], [1, 3, 1], [1, 7, 1], [1, 8, 1],
                   [1, 9, 1], [2, 3, 1], [2, 10, 1], [2, 11, 1], [3, 12, 1], [3, 13, 1]]
}


def test_molecule():
    molecule = Molecule(**mol)
    assert molecule.geometry.flatten().tolist() == mol['geometry']
    for con_mol, con_raw in zip(molecule.connectivity, mol['connectivity']):
        assert list(con_mol) == list(con_raw)
    assert molecule.symbols == mol['symbols']
    assert all(Molecule.parse_raw(molecule.json()).geometry == molecule.geometry)
