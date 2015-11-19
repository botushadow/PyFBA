import sys
from fba.external_reactions import uptake_and_secretion_reactions
from lp import load, objective_coefficients


def create_stoichiometric_matrix(reactions_to_run, reactions, compounds, media, biomass_equation,
                                 uptake_secretion={}, verbose=False):
    """Given the reactions data and a list of RIDs to include, build a
    stoichiometric matrix and load that into the linear solver.

    The uptake and secretion reactions (sometimes called boundary reactions) are reactions that allow
    compounds to flow into the media and secreted compounds away from the cell. You can either provide these
    or we will calculate them for you based on your media and reactions.

    We also take this opportunity to set the objective function (as it is a member of the SM).

    :param uptake_secretion: A hash of uptake and secretion reactions that should be added to the model. Calculated if not provided.
    :type uptake_secretion: dict of Reaction
    :param compounds: a dict of the compounds present
    :type compounds: dict
    :param reactions: a dict of all the reactions
    :type reactions: dict
    :param reactions_to_run: just the reaction ids that we want to include in our model
    :type reactions_to_run: set
    :param media: a set of compounds that would make up the media
    :type media: set
    :param fba: the FBA object
    :type fba: flux_balance_analysis
    :param biomass_equation: the biomass_equation equation as a metabolism.Reaction object
    :type biomass_equation: metabolism.Reaction
    :param verbose: print more information
    :type verbose: bool
    :returns: Sorted lists of all the compunds and reactions in the model, and a revised reactions dict that \
                includes the uptake and secretion reactions
    :rtype : (list, list, dict)
    """

    sm = {}  # the matrix
    allcpds = set()  # all the cpds in the matrix

    # initialize the compounds set and the stoichiometric matrix with
    # everything in the media. The order of compounds is irrelevant
    for c in media:
        if str(c) not in compounds:
            compounds[str(c)] = c
        allcpds.add(str(c))
        sm[str(c)] = {}

    # iterate through the reactions
    for r in reactions_to_run:
        for c in reactions[r].left_compounds:
            allcpds.add(str(c))
            if str(c) not in sm:
                sm[str(c)] = {}
            sm[str(c)][r] = 0 - reactions[r].get_left_compound_abundance(c)

        for c in reactions[r].right_compounds:
            allcpds.add(str(c))
            if str(c) not in sm:
                sm[str(c)] = {}
            sm[str(c)][r] = reactions[r].get_right_compound_abundance(c)

    for c in biomass_equation.left_compounds:
        if str(c) not in compounds:
            compounds[str(c)] = c
        allcpds.add(str(c))
        if str(c) not in sm:
            sm[str(c)] = {}
        sm[str(c)]["BIOMASS_EQN"] = 0 - biomass_equation.get_left_compound_abundance(c)
    for c in biomass_equation.right_compounds:
        if str(c) not in compounds:
            compounds[str(c)] = c
        allcpds.add(str(c))
        if str(c) not in sm:
            sm[str(c)] = {}
        sm[str(c)]["BIOMASS_EQN"] = biomass_equation.get_right_compound_abundance(c)

    # Add the uptake/secretion reactions. These are reactions that allow things to flow from the media
    # into the reaction, or from the cell outwards.
    #
    # The reactions are determined by the external compounds (and biomass_equation), but we only add the left side of the
    # equation to the stoichiometric matrix. This means that they can appear and disappear at will!
    #
    # When we set the reaction bounds we determine which things are in the media unless they are provided for you

    if not uptake_secretion:
        uptake_secretion = uptake_and_secretion_reactions(allcpds, compounds)
    for r in uptake_secretion:
        reactions[uptake_secretion[r].name] = uptake_secretion[r]
        for c in uptake_secretion[r].left_compounds:
            allcpds.add(str(c))
            if str(c) not in sm:
                sm[str(c)] = {}
            sm[str(c)][uptake_secretion[r].name] = 0 - uptake_secretion[r].get_left_compound_abundance(c)

    # now we need to make this into a matrix sorted by
    # reaction id and by cpds
    cp = list(allcpds)
    cp.sort()
    rc = list(reactions_to_run)
    rc.sort()
    rc += [uptake_secretion[x].name for x in uptake_secretion]

    # it is important that we add these at the end
    rc.append("BIOMASS_EQN")

    if verbose:
        sys.stderr.write(sys.argv[0] + ": " + str(len(cp)) + " compounds and " + str(len(rc)) + " reactions\n")

    # here we create the matrix from our sm hash
    data = []
    for i, j in enumerate(cp):
        if j not in sm:
            sys.exit("Error while parsing: no " + j + " in sm")
        data.append([])
        for c in rc:
            if c in sm[j]:
                data[i].append(sm[j][c])
            else:
                data[i].append(0.0)

    # load the data into the model
    load(data, cp, rc)

    # now set the objective function.It is the biomass_equation
    # equation which is the last reaction in the network
    ob = []
    for i in rc:
        ob.append(0.0)
    ob[-1] = 1

    objective_coefficients(ob)

    return cp, rc, reactions