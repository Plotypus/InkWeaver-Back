// To use: 
// mongo < fake_data.js

use inkweaver
db.dropDatabase()

db.users.insert({
    '_id': 'default_user',
    'username': 'user123',
    'password': 'password',
    'name': 'Joe Schmoe',
    'email': 'user123@email.com',
    'pen_name': 'Schmozo',
    'avatar': null,
    'stories': ['default_story'],
    'wikis': ['default_wiki'],
    'preferences': null,
    'statistics': null,
    'bio': null
})

db.stories.insert({
    '_id': 'default_story',
    'owner': {
        'user_id': 'default_user',
        'publication_name': 'Schmoman'
    },
    'wiki_id': 'default_wiki',
    'collaborators': [],
    'title': 'Greatest Story Ever Written',
    'synopsis': 'Need I say more?',
    'head_chapter': 'default_chapter1',
    'tail_chapter': 'default_chapter2',
    'statistics': null,
    'settings': null
})

db.chapters.insert({
    '_id': 'default_chapter1',
    'story_id': 'default_story',
    'title': 'First Chapter',
    'head_paragraph': 'default_paragraph1',
    'tail_paragraph': 'default_paragraph3',
    'preceded_by': null,
    'succeeded_by': 'default_chapter2',
    'statistics': null
})

db.chapters.insert({
    '_id': 'default_chapter2',
    'story_id': 'default_story',
    'title': 'Second Chapter',
    'head_paragraph': 'default_paragraph4',
    'tail_paragraph': 'default_paragraph4',
    'preceded_by': 'default_chapter1',
    'succeeded_by': null,
    'statistics': null
})

db.paragraphs.insert({
    '_id': 'default_paragraph1',
    'chapter_id': 'default_chapter1',
    'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam eros nunc, elementum nec rutrum fringilla, aliquet vitae erat. Duis porta dapibus orci et consequat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras non tempus nisi. Donec semper eros quam, ac lacinia nunc condimentum et. Proin vel neque quis lacus consequat laoreet a eget ante. Phasellus id orci sit amet orci tristique suscipit eu vitae enim. Suspendisse at libero et purus bibendum congue eget sodales lorem. Nam tincidunt, diam sed convallis fermentum, nulla nisi ultricies lorem, ut ullamcorper neque urna nec mauris. Integer porta mattis sem. Nulla interdum nisi eget lacus pharetra, consectetur ultricies ante sodales. Cras molestie ut nibh vel cursus. Nam ac porta purus.',
    'statistics': null,
    'preceded_by': null,
    'succeeded_by': 'default_paragraph2'
})

db.paragraphs.insert({
    '_id': 'default_paragraph2',
    'chapter_id': 'default_chapter1',
    'text': 'Morbi volutpat facilisis interdum. Aenean vel porttitor elit. Nullam imperdiet metus eu nisl auctor porta. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Nunc finibus posuere velit vel laoreet. In euismod suscipit porta. Suspendisse lobortis neque eu tempus hendrerit. Vivamus sagittis, ipsum at scelerisque luctus, nibh sapien tempor neque, vel feugiat est odio nec dui. Nulla vel velit nec felis laoreet ultricies id vitae diam. Proin id auctor sem, eget posuere justo. In hac habitasse platea dictumst. Maecenas egestas eros id ligula tempus facilisis.',
    'statistics': null,
    'preceded_by': 'default_paragraph1',
    'succeeded_by': 'default_paragraph3'
})

db.paragraphs.insert({
    '_id': 'default_paragraph3',
    'chapter_id': 'default_chapter1',
    'text': 'Aliquam fermentum tempor augue, vel tincidunt lacus pretium vel. Quisque eu risus tellus. Integer venenatis dolor eu eros rhoncus, eu rutrum tortor tincidunt. Vestibulum euismod, leo in posuere accumsan, felis metus auctor augue, vel ultricies purus diam at augue. Phasellus dolor risus, gravida sit amet vehicula eu, accumsan tempus felis. Curabitur tortor elit, finibus ac aliquam sit amet, finibus nec diam. Praesent finibus purus mi, id tincidunt magna faucibus sed. Nulla scelerisque diam odio, in efficitur odio tempus ut. Donec turpis est, fringilla eu imperdiet at, ultrices ac orci. Donec consequat erat mi, in eleifend augue ornare sed. In hac habitasse platea dictumst. Praesent finibus a urna cursus lacinia.',
    'statistics': null,
    'preceded_by': 'default_paragraph2',
    'succeeded_by': null
})

db.paragraphs.insert({
    '_id': 'default_paragraph4',
    'chapter_id': 'default_chapter2',
    'text': 'Vivamus congue semper gravida. Duis vitae bibendum lacus, vitae bibendum leo. Praesent hendrerit nisl ut posuere pellentesque. Quisque vitae lobortis ante. Morbi eu turpis ipsum. Proin sed nulla ac dui aliquam venenatis sed quis ex. Aliquam non odio velit. Etiam vel tristique urna, congue iaculis dolor. Nulla mollis rhoncus ipsum egestas volutpat. Ut a nulla et ex interdum dapibus at porta nibh. Nulla sed mauris sit amet neque tristique pharetra in sit amet libero.',
    'statistics': null,
    'preceded_by': null,
    'succeeded_by': null
})
