from SystemCore.CatalogCommunication.CataloguesManager import CatalogsManager

CM = CatalogsManager(process_name='test1', parent_directory='E:/0_Data/0 Main catalog')


CM.add_section('S1', 'S1')
CM.add_section('S2', 'S2')
dir = CM.session_path