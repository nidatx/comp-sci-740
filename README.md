# Revisiting the Self Similar Nature of Web Traffic with Modern Browsers and Web pages
To be able to make important decisions about the design of the Internet, it is important to always understand the behavior of network traffic. 
While the self-similar nature of Web traffic is well-established and well-studied, it is still interesting to observe network traffic in light of changes in
the landscape of the Internet. The complexity of web pages and the strategies employed by web browsers are different now. Our project simulates users browsing popular
websites, capture HTTPS traffic and analyze how factors like prefetching, and local caching impact the self-similarity
of web traffic in the context of modern browsers and webpages. 

We use 3 different we browsers: Chrome, Firefox and Edge.

Our main script is the `automate_users.py`. This script launches 3 threads, each one opens a different website and performs actions simulting a real life user.

You can also change the type of web browser you would like to use, currently the `WebsiteAutomator` class supports Chrome, Edge and Firefox. To change the browser type just pass in the desired type when initializing the `WebsiteAutomator` class.

You can see our script in action by running it using `python3 automate_users.py`.

You do need to have the appropraite web drivers installed. We recommed using the 'for testing' versions Chrome/Edge/Firefox since browser updates are frequent and it is difficult to keep up with all these changes in your code.

While you're here, have a look at our [Final Report](https://github.com/nidatx/comp-sci-740/blob/main/Final%20Report.pdf) if you're interested (or maybe just the [Poster](https://github.com/nidatx/comp-sci-740/blob/main/Poster.pdf) if you're interested but short on time).
