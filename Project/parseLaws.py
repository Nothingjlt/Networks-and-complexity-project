import re
import os
from bs4 import BeautifulSoup

# A list of regular expressions expressing a citation to another law or regulation.
# The format should be of a specific word indicating a citation, followed by a hebrew year
# and continued by a Gregorian year.
# The list is based on a manual review of sampled example laws, and were refined to try an filter
# out any garbage. A more relaxed definition can be performed (e.g. more words indicating a citation).
# Anyway a manual review of the output results is advised to confirm all results indeed indicate
# a citation.
CITATION_RES = dict(
    COMMANDS_RE='פקודה.*?[ה]?תש[א-ת"]{1,2}.*?[0-9]{4}',
    COMMANDS2_RE='פקודת.*?[ה]?תש[א-ת"]{1,2}.*?[0-9]{4}',
    COMMANDS3_RE='פקודות.*?[ה]?תש[א-ת"]{1,2}.*?[0-9]{4}',
    LAWS_RE='חוק.*?[ה]?תש[א-ת"]{1,2}.*?[0-9]{4}',
    REGULATIONS_RE='תקנה.*?[ה]?תש[א-ת"]{1,2}.*?[0-9]{4}',
    REGULATIONS2_RE='תקנת.*?[ה]?תש[א-ת"]{1,2}.*?[0-9]{4}',
    REGULATIONS3_RE='תקנות.*?[ה]?תש[א-ת"]{1,2}.*?[0-9]{4}',
    INSTRUCTIONS_RE='הוראה.*?[ה]?תש[א-ת"]{1,2}.*?[0-9]{4}',
    INSTRUCTIONS2_RE='הוראת.*?[ה]?תש[א-ת"]{1,2}.*?[0-9]{4}',
    INSTRUCTIONS3_RE='הוראות.*?[ה]?תש[א-ת"]{1,2}.*?[0-9]{4}',
)

# A list of regular expressions expressing an action being performed in the law.
# The regular expressions look for specific words that indicate an action, followed by an
# end of word signal (either whitespace, comma, colon or period)
# The list of actions is based on a manual review of a sample of example laws. It is
# advised to complete the list with additional potential actions (or additional potential
# Hebrew phrasing of actions).
ACTION_RES = dict(
    INSTRUCTED_RE='הורה[ .;,\s]',
    INSTRUCTED2_RE='הנחה[ .;,\s]',
    OVERSAW_RE='פיקח[ .;,\s]',
    SET_RE='קבע[ .;,\s]',
    APPROVED_RE='אישר[ .;,\s]',
    ALLOWED_RE='התיר[ .;,\s]',
    SET2_RE='הכריע[ .;,\s]',
)

# A list of regular expressions expressing entities mentioned in laws.
# The format of the regular expression is to match potential entities. In the case of
# construct states, the word indicating an entity (e.g. מפקח) is expected to have an
# additional word after it, in an attempt to filter out actions that are indicated
# by the same Hebrew word.
ENTITIES_RES = dict(
    SUPERVISOR_RE='מפקח ה.*?[ .;,\s]',
    SUPERVISOR2_RE='מפקח על .*?[ .;,\s]',
    SUPERIOR_RE='ממונה על .*?[ .;,\s]',
    TESTER_RE='ה?בודק ה?מוסמך',
    BUILDER_RE='ה?בונה ה?מקצועי',
    CONTRACTOR_RE='מבצע ה?בניה',
    CONTRACTOR2_RE='קבלן',
    INSPECTION_INSTITUTE_RE='מוסד ה?ביקורת ה?מוסמך',
    PLANNER_RE='מתכנן .*?[ .;,\s]',
    SIGNALING_PERSON_RE='ה?מוסמך למתן איתות',
    EMPLOYER_RE='ה?מעסיק',
)

# The citation regular expressions may result in very long strings, that are assumed
# to be false positives of the match. Limiting the length of potential citations
# proved to be an effective additional filter.
LONGEST_POSSIBLE_CITATION_LENGTH = 200

# Apparently some of the laws in HTML format have unnecessary unicode characters.
# '\u2003' is another way to write ' ', '\u03bc' is a unicode character for the
# lower case Greek letter mu, and '\xfc' is probably meant to be u diaeresis.
# All should be safe to ignore in the context of Hebrew test parsing.
UNICODE_CHARS_TO_IGNORE = ['\u2003', '\u03bc', '\xfc']

# The relative path location of the directory containing all laws in HTML format.
# The path should be relative to the current directory from which this code is being run.
DIRECTORY_TO_PARSE = r'..\Laws\HTML'

# The relative path location of the expected out directory to which output files
# should be written.
OUTPUT_DICTIONARY = r'..\Laws\HTML\out'

# A list of output files to be created.
OUTPUT_FILES = dict(
    ENTITIES_CONNECTED_BY_ACTIONS='entities_connected_by_actions.csv',
    ENTITIES_LAWS_BIPARTITE='entities_laws_bipartite.csv',
    ENTITIES_CITATIONS_BIPARTITE='entities_citations_bipartite.csv',
    LAWS_CITATIONS_BIPARTITE='laws_citations_bipartite.csv',
    ENTITIES_FILENAME='entities.csv',
    CITATIONS_FILENAME='citations.csv',
    LAWS_FILENAME='laws.csv',
    ACTIONS_FILENAME='actions.csv',
)

# Used for bi-partite plot in Gephi. Each node type has its own X axis coordinate.
X_COORDINATES = dict(
    ACTIONS_X=10,
    ENTITIES_X=20,
    LAWS_X=30,
    CITATIONS_X=40,
)


def apply_filter_on_text(txt, filters):
    """Apply a list of regular expression patterns on a given text, returning a combined list of all results from all
    the patterns on the list.

    :param txt: A string with the text to apply the filters on
    :param filters: A dictionary who's values are the regular expression patterns to apply
    :return: A list of all results from all regular expression patterns
    """
    results = []
    for pattern in filters.values():
        results = results + (re.findall(pattern, txt, re.S))
    return results


def get_citations_from_text(txt):
    """Apply all citation regular expressions on a given string.

    :param txt: A string to apply the citation regular expressions on
    :return: A list of all matches of citation regular expressions on txt
    """
    return apply_filter_on_text(txt, CITATION_RES)


def get_actions_from_text(txt):
    """Apply all action regular expressions on a given string.

    :param txt: A string to apply the action regular expressions on
    :return: A list of all matches of action regular expressions on txt
    """
    return apply_filter_on_text(txt, ACTION_RES)


def get_entities_from_test(txt):
    """Apply all entities regular expressions on a given string.

    :param txt: A string to apply the entities regular expressions on
    :return: A list of all matches of entities regular expressions on txt
    """
    return apply_filter_on_text(txt, ENTITIES_RES)


def remove_weird_unicode(txt):
    """Replace all unicode characters defined in UNICODE_CHARS_TO_IGNORE with white space.

    :param txt: A string to replace the unicode characters in
    :return: The string after replacing the unicode characters
    """
    for c in UNICODE_CHARS_TO_IGNORE:
        txt = txt.replace(c, ' ')
    return txt


def clean_list_item(item):
    """There are several cases where the original text contains multiple consecutive newlines.

    This function replaces such newlines with a single white space.
    This allows storing the output text in csv format since newlines in a certain node's definition would artificially
    create a new node which should not have existed.
    Any number of consecutive newlines will be replaced with only one whitespace.

    :param item: A string to remove consecutive newlines from
    :return: item with all consecutive newlines replaced with whitespaces
    """
    return re.sub('\n+', ' ', item)


def write_list_out(fout, enum):
    """Encode a list of strings into 'utf-8' and write the list with newline separator

    :param fout: The output file to write the list to. Should have write permissions
    :param enum: The list of strings to write
    :return: None
    """
    for e in enum:
        fout.write((clean_list_item(e) + '\r\n').encode('utf-8'))
    return


def remove_trailing_chars(s):
    """Remove trailing characters from a string.

    There are some strings with many trailing characters, that appear after the Hebrew text. Trailing characters that
    are being removed are: '.', ',', ':', '"', '[', ']', ':' and any whitespace (' ', '\t', etc.)

    :param s: String to remove trailing characters from
    :return: The string without trailing characters
    """
    return re.sub('[.,;"\[\]\s:]+$', '', s)


def write_to_fout_txt(law_name, details):
    """Write all details about a specific law to an output file.

    The function writes all details of the input law to an output file with the same name as the law, after replacing
    the *.htm extension with *.out.txt.
    The output file should be available to open with write permissions. The file will be closed before the function
    returns.
    The output file format will be as following:
    ציטוטים
    <a list of citations that appear in the law, separated by newlines>

    פעולות
    <a list of action that appear in the law, separated by newlines>

    גופים
    <a list of entities that appear in the law, separated by newlines>

    :param law_name: A string name of the law of which to write the output details
    :param details: A dictionary with the following keys: 'citations', 'actions', 'entities', each one containing an
        enumerable of strings representing the appearance of a specific node in the law_name input law.
    :return: None
    """
    fout = open(os.path.join(OUTPUT_DICTIONARY, law_name.replace('htm', 'out.txt')), 'wb')
    fout.write('ציטוטים\r\n'.encode('utf-8'))
    write_list_out(fout, details['citations'])
    fout.write('\r\n\r\n'.encode('utf-8'))
    fout.write('פעולות\r\n'.encode('utf-8'))
    write_list_out(fout, details['actions'])
    fout.write('\r\n\r\n'.encode('utf-8'))
    fout.write('גופים\r\n'.encode('utf-8'))
    write_list_out(fout, details['entities'])
    fout.close()
    return


def write_to_fout_entities_actions(details):
    """Gets all entities in a specific law, and writes an adjacency list based on common appearance of entities in
    the specific law.

    For any pair of entities mentioned in the same law, a number of lines indicating their adjacency is appended to the
    output file. The number of lines added to the the output file is determined by the number of actions mentioned in
    the same law.
    This logic is intended to indicate that entities that are mentioned with many actions in the same law should
    probably have a stronger connection than entities mentioned without any actions in the same law.
    There is of course no guarantee that mentioning two entities in the same law actually means they are adjacent for
    our purposes, but this is an estimate that is possible to make even without applying advanced NLP techniques.

    The output file name is defined under OUTPUT_FILES['ENTITIES_CONNECTED_BY_ACTIONS'].
    The file is opened with append permissions and is closed before the function returns.

    The adjacency list is being updated with each call, so details from multiple laws can be accumulated in one output
    file.
    The function is intended to be called consecutively on all details of all input laws.

    :param details: A dictionary with the keys: 'entities', 'actions'. Should indicate the entities and actions
        mentioned together in the same law.
    :return: None
    """
    fout = open(os.path.join(OUTPUT_DICTIONARY, OUTPUT_FILES['ENTITIES_CONNECTED_BY_ACTIONS']), 'ab')
    out_list = []
    for entity in set(details['entities']):
        for entity2 in set(details['entities']):
            if entity == entity2:
                continue
            for action in set(details['actions']):
                out_list.append(f'{entity}\t{entity2}')
    write_list_out(fout, out_list)
    fout.close()
    return


def write_to_fout_entities_laws(law_name, details):
    """Writes an adjacency list between the law and the entities mentioned in it.

    For any entity mentioned in a certain law, a line is appended to the output file indicating an adjacency.
    This logic is intended to indicate that the same entity may appear in different laws, and a certain law may have
    different entities mentioned in it.
    The resulting file can be used to generate a bipartite graph between laws and entities.

    The output file name is defined under OUTPUT_FILES['ENTITIES_LAWS_BIPARTITE'].
    The file is opened with append permissions and is closed before the function returns.

    The adjacency list is being updated with each call, so details from multiple laws can be accumulated in one output
    file.
    The function is intended to be called consecutively on all details of all input laws.

    :param law_name: A string indicating the specific law's name
    :param details: A dictionary with the key: 'entities'. Should indicate the entities mentioned the law.
    :return: None
    """
    fout = open(os.path.join(OUTPUT_DICTIONARY, OUTPUT_FILES['ENTITIES_LAWS_BIPARTITE']), 'ab')
    out_list = []
    for entity in set(details['entities']):
        out_list.append(f'{entity}\t{law_name}')
    write_list_out(fout, out_list)
    fout.close()
    return


def write_to_fout_entities_citations(details):
    """Writes an adjacency list between entities and citations mentioned in the same law.

    For any pair of entity-citation mentioned in the same law, a line is appended to the output file indicating an
    adjacency between the two.
    This logic is intended to complement the entities-laws list that is generated by write_to_fout_entities_laws.

    The links generated by this function are probably weaker than those of write_to_fout_entities_laws, since a joint
    appearance in a law does not necessarily mean that the two are connected.

    The output file name is defined under OUTPUT_FILES['ENTITIES_CITATIONS_BIPARTITE'].
    The file is opened with append permissions and is closed before the function returns.

    The adjacency list is being updated with each call, so details from multiple laws can be accumulated in one output
    file.
    The function is intended to be called consecutively on all details of all input laws.

    :param details: A dictionary with the keys: 'entities', 'citations'. Should indicate the entities and citations
        mentioned together in the same law.
    :return: None
    """
    fout = open(os.path.join(OUTPUT_DICTIONARY, OUTPUT_FILES['ENTITIES_CITATIONS_BIPARTITE']), 'ab')
    out_list = []
    for entity in set(details['entities']):
        for citation in set(details['citations']):
            out_list.append(f'{entity}\t{citation}')
    write_list_out(fout, out_list)
    fout.close()


def write_to_fout_laws_citations(law_name, details):
    """Writes an adjacency list between the law and the citations mentioned in it.

    For any citation mentioned in a certain law, a line is appended to the output file indicating an adjacency.
    This logic is intended to generate the citation graph of laws in the field, including references to laws outside of
    the pool in the input folder.

    The output file name is defined under OUTPUT_FILES['LAWS_CITATIONS_BIPARTITE'].
    The file is opened with append permissions and is closed before the function returns.

    The adjacency list is being updated with each call, so details from multiple laws can be accumulated in one output
    file.
    The function is intended to be called consecutively on all details of all input laws.

    :param law_name: A string indicating the specific law's name
    :param details: A dictionary with the key: 'citations'. Should indicate the citations mentioned the law.
    :return: None
    """
    fout = open(os.path.join(OUTPUT_DICTIONARY, OUTPUT_FILES['LAWS_CITATIONS_BIPARTITE']), 'ab')
    out_list = []
    for citation in set(details['citations']):
        out_list.append(f'{law_name}\t{citation}')
    write_list_out(fout, out_list)
    fout.close()
    return


def iter_to_list_of_strings(iterable, x_coord):
    """Generates a list of strings to be written to an output file in csv format.

    Supposed to be used for bipartite graphs, where each node should have both X and Y coordinates.
    The X coordinate of all nodes in the iterable is determined as an input, and Y coordinate is determined by the index
    of each iterable.

    The output is a list of strings, where each item in the list is in the format:
    <item name>\t<X coordinate>\t<Y coordinate>
    Where the first item in the list is a header:
    Id\tx_coord\ty_coord

    :param iterable: An iterable containing strings to which coordinates need to be assigned
    :param x_coord: A constant X coordinate for all items in iterable
    :return: A list of strings, where each item corresponds to an item in iterable, with its X and Y coordinates
    """
    l = [f"Id\tx_coord\ty_coord"]
    for idx, item in enumerate(iterable):
        l.append(f"{item}\t{x_coord}\t{idx + 1}")
    return l


def write_all_actions(actions):
    """Writes all actions in all laws to an output file.

    The list of actions is written to the output file in the format as received from iter_to_list_of_strings, where each
    item in iter_to_list_of_strings's returned list is written in a new line.

    The output file name is defined under OUTPUT_FILES['ACTIONS_FILENAME'].
    The file is opened with write permissions and is closed before the function returns.

    :param actions: A list of all actions mentioned in all laws
    :return: None
    """
    fout = open(os.path.join(OUTPUT_DICTIONARY, OUTPUT_FILES['ACTIONS_FILENAME']), 'wb')
    clean_list = map(clean_list_item, actions)
    write_list_out(fout, iter_to_list_of_strings(set(clean_list), X_COORDINATES['ACTIONS_X']))
    fout.close()
    return


def write_all_entities(entities):
    """Writes all entities in all laws to an output file.

    The list of entities is written to the output file in the format as received from iter_to_list_of_strings, where
    each item in iter_to_list_of_strings's returned list is written in a new line.

    The output file name is defined under OUTPUT_FILES['ENTITIES_FILENAME'].
    The file is opened with write permissions and is closed before the function returns.

    :param entities: A list of all entities mentioned in all laws
    :return: None
    """
    fout = open(os.path.join(OUTPUT_DICTIONARY, OUTPUT_FILES['ENTITIES_FILENAME']), 'wb')
    clean_list = map(clean_list_item, entities)
    write_list_out(fout, iter_to_list_of_strings(set(clean_list), X_COORDINATES['ENTITIES_X']))
    fout.close()
    return


def write_all_citations(citations):
    """Writes all citations in all laws to an output file.

    The list of citations is written to the output file in the format as received from iter_to_list_of_strings, where
    each item in iter_to_list_of_strings's returned list is written in a new line.

    The output file name is defined under OUTPUT_FILES['CITATIONS_FILENAME'].
    The file is opened with write permissions and is closed before the function returns.

    :param citations: A list of all citations mentioned in all laws
    :return: None
    """
    fout = open(os.path.join(OUTPUT_DICTIONARY, OUTPUT_FILES['CITATIONS_FILENAME']), 'wb')
    clean_list = map(clean_list_item, citations)
    write_list_out(fout, iter_to_list_of_strings(set(clean_list), X_COORDINATES['CITATIONS_X']))
    fout.close()
    return


def write_all_laws(laws):
    """Writes all laws names to an output file.

    The list of laws is written to the output file in the format as received from iter_to_list_of_strings, where each
    item in iter_to_list_of_strings's returned list is written in a new line.

    The output file name is defined under OUTPUT_FILES['LAWS_FILENAME'].
    The file is opened with write permissions and is closed before the function returns.

    :param laws: A list of all laws in the input folder
    :return: None
    """
    fout = open(os.path.join(OUTPUT_DICTIONARY, OUTPUT_FILES['LAWS_FILENAME']), 'wb')
    clean_list = map(clean_list_item, laws)
    write_list_out(fout, iter_to_list_of_strings(set(clean_list), X_COORDINATES['LAWS_X']))
    fout.close()
    return


def write_to_fout(law_name, details):
    """Writes all details of a certain laws to the relevant output files.

    For each law, call all the relevant write_to_fout_* functions with the relevant details.

    :param law_name: The name of the law of which the details should be written out
    :param details: A dictionary with the keys: 'actions', 'citations', 'entities', each containing a list of all
        actions, citations and entities mentioned in the specific law
    :return: None
    """
    write_to_fout_txt(law_name, details)
    write_to_fout_entities_actions(details)
    write_to_fout_entities_laws(law_name, details)
    write_to_fout_entities_citations(details)
    write_to_fout_laws_citations(law_name, details)
    return


def parse_laws():
    """The main logic of the code.

    This function iterates over all files in the input directory (each containing a law), extracts their HTML body
    (keeping only text), and finds within each law the citations, entities and actions mentioned in it.

    :return: A tuple of:
        1. A dictionary mapping each law name to its "details" structure, which is a dictionary containing the keys:
        'citations', 'actions', 'entities', pointing to the list of citations, actions and entities respectively.
        2. A set of all actions mentioned in all laws in the input folder
        3. A set of all entities mentioned in all laws in the input folder
        4. A set of all citations mentioned in all laws in the input folder
    """
    tot_cites = 0
    tot_actions = 0
    tot_entities = 0
    all_entities = set()
    all_actions = set()
    all_citations = set()
    laws = {}
    for d in os.scandir(DIRECTORY_TO_PARSE):
        if not d.is_file() or not d.name.endswith('htm'):
            continue
        laws[d.name] = {}
        print(d.name)
        f = open(d.path)
        soup = BeautifulSoup(f, features="lxml")
        txt = soup.body.get_text()
        txt = remove_weird_unicode(txt)
        txt = txt.encode('windows-1252').decode('windows-1255')
        citations = get_citations_from_text(txt)
        actions = sorted(map(remove_trailing_chars, get_actions_from_text(txt)))
        entities = sorted(map(remove_trailing_chars, get_entities_from_test(txt)))
        laws[d.name]['citations'] = list(filter(lambda x: len(x) < LONGEST_POSSIBLE_CITATION_LENGTH, sorted(citations)))
        laws[d.name]['actions'] = actions
        laws[d.name]['entities'] = entities
        all_actions.update(set(laws[d.name]['actions']))
        all_entities.update(set(laws[d.name]['entities']))
        all_citations.update(set(laws[d.name]['citations']))
        tot_cites += len(citations)
        tot_actions += len(actions)
        tot_entities += len(entities)
    print(
        f'Total cites: {tot_cites}, '
        f'total actions: {tot_actions}, '
        f'total entities: {tot_entities}'
    )
    return laws, all_actions, all_entities, all_citations


def clear_old_files():
    """Delete files output files from previous runs, to allow for a clean new run.

    Files that are deleted are specified in OUTPUT_FILES

    :return: None
    """
    for f in OUTPUT_FILES.values():
        file_to_remove = os.path.join(OUTPUT_DICTIONARY, f)
        open(file_to_remove, 'w')
        os.remove(file_to_remove)


def main():
    """The main function of the module. Clears all old files, parses laws in the input directory and writes all output
    files.

    :return: None
    """
    clear_old_files()
    laws, all_actions, all_entities, all_citations = parse_laws()
    for law, details in laws.items():
        write_to_fout(law, details)
        print(
            f'File: {law}, '
            f'Number of citations: {len(details["citations"])}, '
            f'number of actions: {len(details["actions"])}, '
            f'number of entities: {len(details["entities"])}'
        )
    print(f'Num of actions: {len(all_actions)}, num of entities: {len(all_entities)}')
    write_all_actions(all_actions)
    write_all_entities(all_entities)
    write_all_citations(all_citations)
    write_all_laws(laws.keys())
    print(all_entities)


if __name__ == '__main__':
    main()
