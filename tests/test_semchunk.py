"""Test semchunk."""
import semchunk
import tiktoken

LOREM = """\
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Id porta nibh venenatis cras sed felis eget velit. Et tortor consequat id porta nibh. Id diam vel quam elementum pulvinar. Consequat nisl vel pretium lectus quam id. Pharetra magna ac placerat vestibulum lectus mauris ultrices eros in. Id velit ut tortor pretium viverra. Tempus imperdiet nulla malesuada pellentesque elit eget gravida. In est ante in nibh mauris cursus mattis molestie a. Risus quis varius quam quisque id. Lorem ipsum dolor sit amet consectetur. Non nisi est sit amet facilisis magna. Leo in vitae turpis massa sed elementum tempus egestas sed. Luctus venenatis lectus magna fringilla urna porttitor rhoncus dolor. At erat pellentesque adipiscing commodo. Sagittis orci a scelerisque purus. Condimentum vitae sapien pellentesque habitant morbi tristique senectus et netus. A cras semper auctor neque vitae tempus quam pellentesque.
\n\r\t\v\f
Facilisi cras fermentum odio eu feugiat. Sit amet consectetur adipiscing elit pellentesque habitant morbi tristique senectus. Nulla posuere sollicitudin aliquam ultrices sagittis orci a scelerisque purus. Enim ut sem viverra aliquet eget sit amet tellus cras. Non arcu risus quis varius quam quisque id. Purus in mollis nunc sed id. Lorem sed risus ultricies tristique nulla aliquet enim. Diam in arcu cursus euismod quis viverra. Et sollicitudin ac orci phasellus egestas tellus rutrum tellus. Ac ut consequat semper viverra nam libero justo laoreet sit. Mattis ullamcorper velit sed ullamcorper morbi tincidunt ornare. Netus et malesuada fames ac turpis egestas. Sed enim ut sem viverra aliquet eget sit amet. In iaculis nunc sed augue lacus viverra vitae congue.

Nunc consequat interdum varius sit amet mattis vulputate enim. Pulvinar pellentesque habitant morbi tristique. Viverra ipsum nunc aliquet bibendum enim. Egestas erat imperdiet sed euismod nisi porta lorem mollis. Mattis rhoncus urna neque viverra justo nec. Dictum non consectetur a erat nam at lectus. Tincidunt arcu non sodales neque. Sagittis eu volutpat odio facilisis mauris. Nec nam aliquam sem et tortor consequat id porta. Nulla pellentesque dignissim enim sit amet venenatis urna. Eget magna fermentum iaculis eu non diam phasellus. Leo in vitae turpis massa sed elementum. Libero volutpat sed cras ornare arcu dui vivamus. Molestie nunc non blandit massa enim nec dui nunc mattis. Odio facilisis mauris sit amet massa vitae tortor. Ullamcorper velit sed ullamcorper morbi tincidunt ornare. Nec dui nunc mattis enim ut.

Id volutpat lacus laoreet non curabitur gravida arcu. Pulvinar proin gravida hendrerit lectus a. Id neque aliquam vestibulum morbi blandit cursus. Quam nulla porttitor massa id neque aliquam vestibulum morbi. Urna et pharetra pharetra massa massa ultricies. Sed enim ut sem viverra aliquet. Quam quisque id diam vel quam elementum pulvinar etiam non. Urna molestie at elementum eu facilisis sed odio morbi quis. Commodo sed egestas egestas fringilla phasellus faucibus scelerisque eleifend donec. Pharetra magna ac placerat vestibulum lectus mauris ultrices eros.

Quam quisque id diam vel quam elementum pulvinar. Pellentesque habitant morbi tristique senectus et netus et. Tellus in metus vulputate eu scelerisque felis. Facilisis sed odio morbi quis. Dictum sit amet justo donec enim diam. A diam maecenas sed enim ut sem viverra aliquet eget. Phasellus vestibulum lorem sed risus ultricies tristique nulla aliquet. Non odio euismod lacinia at quis risus sed vulputate odio. Et netus et malesuada fames ac turpis egestas maecenas. Scelerisque viverra mauris in aliquam sem fringilla ut. Ac odio tempor orci dapibus. Lectus vestibulum mattis ullamcorper velit sed ullamcorper morbi."""

def _token_counter(text: str) -> int:
    return len(tiktoken.encoding_for_model('gpt-4').encode(text))

def test_chunk():
    # Test a variety of chunk sizes.
    for chunk_size in range(1,100):
        for chunk in semchunk.chunk(LOREM, chunk_size=chunk_size, token_counter=_token_counter):
            assert _token_counter(chunk) <= 1
    
    # Test a chunk size larger than the text.
    semchunk.chunk(LOREM, chunk_size=len(LOREM)**2, token_counter=_token_counter)