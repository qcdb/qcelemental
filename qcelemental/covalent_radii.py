"""
Contains covalent radii
"""

import collections
from decimal import Decimal
from typing import Dict, Union

from .datum import Datum, print_variables
from .exceptions import DataUnavailableError
from .periodic_table import periodictable


class CovalentRadii:
    r"""Covalent radii sets.

    Parameters
    ----------
    context : str
        {'ALVAREZ2008'}
        Origin of loaded data.

    Attributes
    ----------
    cr : Dict[str, Datum]
        Each covalent radius is an entry in `cr`, where key is the
        "Fe"-cased element symbol if generic or symbol-prefixed label
        if specialized within element. The value is a Datum object with
        `lbl` the same as key, `units`, `data` value as Decimal object,
        and any uncertainty in the `comment` field.
    doi : str
        The DOI of the current context.
    name : str
        The name of the context ('ALVAREZ2008')
    native_units : str
        The units the original data was provided in.
    year : int
        The year the context was created.

    """

    def __init__(self, context: str = "ALVAREZ2008"):
        self.cr: Dict[str, Datum] = collections.OrderedDict()

        from .data import alvarez_2008_covalent_radii

        if context == "ALVAREZ2008":
            self.doi = alvarez_2008_covalent_radii["doi"]
            self.native_units = alvarez_2008_covalent_radii["units"]

            # TypedDict wont be in until 3.8, have to ignore heterogeneous dicts for now
            for cr in alvarez_2008_covalent_radii["covalent_radii"]:  # type: ignore
                self.cr[cr[0]] = Datum(cr[0], self.native_units, Decimal(cr[1]), comment=cr[2], doi=self.doi)
        else:
            raise KeyError(f"Context set as '{context}', " + "only contexts {'ALVAREZ2008', } are currently supported")

        self.name = context
        self.year = int(alvarez_2008_covalent_radii["date"][:4])  # type: ignore

        # Extra relationships
        aliases = [
            ("C", "angstrom", self.cr["C_sp3"].data, "Largest (sp3) chosen for generic atom"),
            ("Mn", "angstrom", self.cr["Mn_highspin"].data, "Larger (high-spin) chosen for generic atom"),
            ("Fe", "angstrom", self.cr["Fe_highspin"].data, "Larger (high-spin) chosen for generic atom"),
            ("Co", "angstrom", self.cr["Co_highspin"].data, "Larger (high-spin) chosen for generic atom"),
        ]  # yapf: disable

        # add alternate names to help QC programs
        for alias in aliases:
            ident, units, value, comment = alias
            self.cr[ident.capitalize()] = Datum(ident, units, value, comment=comment)

    def __str__(self) -> str:
        return "CovalentRadii(context='{}')".format(self.name)

    def get(
        self, atom: Union[int, str], *, return_tuple: bool = False, units: str = "bohr", missing: float = None
    ) -> Union[float, "Datum"]:  # lgtm [py/similar-function]
        r"""
        Access a covalent radius for species `atom`.

        Parameters
        ----------
        atom
            Identifier for element or nuclide, e.g., ``H``, ``D``, ``H2``, ``He``, ``hE4``.
            In general, one value recommended for each element; however, certain other exact labels may be available.
            ALVAREZ2008: C_sp3, C_sp2, C_sp, Mn_lowspin, Mn_highspin, Fe_lowspin, Fe_highspin, Co_lowspin, Co_highspin
        units
            Units of returned value. To return in native unit (ALVAREZ2008: angstrom), pass it explicitly.
            Only relevant for ``return_tuple=False`` since ``True`` returns underlying data structure with native units.
        missing
            How to handle when ``atom`` is valid but outside the available data range. When ``None``, raises DataUnavailableError.
            When a float, returns that float, so supply in ``units`` units. Supplying a float is a more compact assurance
            that a call will work over all the periodic table than the equivalent

            .. code-block:: python

                try:
                    rad = qcel.covalentradii.get(atom)
                except qcel.DataUnavailableError:
                    rad = 4.0

            Only relevant for ``return_tuple=False``.
        return_tuple
            See below.

        Returns
        -------
        float
            When ``return_tuple=False``, value of covalent radius. If multiple defined for element, returns largest.
        qcelemental.Datum
            When ``return_tuple=True``, Datum with units, description, uncertainty, and value of covalent radius as Decimal (preserving significant figures).
            If multiple defined for element, returns largest.

        Raises
        ------
        NotAnElementError
            If `atom` cannot be resolved into an element or nuclide or label.
        DataUnavailableError
            If `atom` is a valid element or nuclide but not one for which a covalent radius is available and `missing=None`.

        """
        if atom in self.cr.keys():
            # catch extra labels like 'C_sp3'
            identifier = atom
        else:
            identifier = periodictable.to_E(atom)

        try:
            assert isinstance(identifier, str)  # Should be string by now
            qca = self.cr[identifier]
        except KeyError as e:
            if missing is not None and return_tuple is False:
                return missing
            else:
                raise DataUnavailableError("covalent radius", identifier) from e

        if return_tuple:
            return qca
        else:
            return qca.to_units(units)

    def string_representation(self) -> str:
        """Print name, value, and units of all covalent radii."""

        return print_variables(self.cr)

    def write_c_header(self, filename: str = "covrad.h", missing: float = 2.0) -> None:  # lgtm[py/similar-function]
        r"""Write C header file defining covalent radii array.

        Parameters
        ----------
        filename
            File name for header. Note that changing this won't change the header guard.
        missing
            In order that the C array be atomic-number indexable and that it span the
            periodic table, this value is used anywhere data is missing.

        """
        text = [
            "#ifndef _qcelemental_covrad_h_",
            "#define _qcelemental_covrad_h_",
            "",
            "/* This file is autogenerated from the QCElemental python module */",
            "",
            "const double covalent_radii[] = {",
        ]

        for el in periodictable.E:
            try:
                qca = self.cr[el]
                text.append("{},  /*- [{}] {} {} -*/".format(qca.data, qca.units, qca.label, qca.comment))
            except KeyError:
                text.append(
                    "{:.2f},  /*- [{}] {} {} -*/".format(
                        missing, self.native_units, el, "Default value for missing data"
                    )
                )

        text.append("};")
        text.append("#endif /* header guard */")
        text.append("")

        with open(filename, "w") as handle:
            handle.write("\n".join(text))
        print("File written ({}). Remember to add license and clang-format it.".format(filename))


# singleton
covalentradii = CovalentRadii("ALVAREZ2008")
