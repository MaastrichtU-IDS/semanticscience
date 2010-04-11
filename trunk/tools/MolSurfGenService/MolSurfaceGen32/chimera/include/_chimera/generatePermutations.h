
template <class Item>
void
generatePermutations(std::vector<Item *> &items,
				std::vector<std::vector<Item *> > *permutations)
{
	std::vector<typename std::vector<Item *> > lastGen;
	std::vector<typename std::vector<Item *>::iterator> lastRems;
	for (typename std::vector<Item *>::iterator ii = items.begin();
	ii != items.end(); ++ii ) {
		Item *i = *ii;
		std::vector<Item *> itemList;
		itemList.push_back(i);
		lastGen.push_back(itemList);
		lastRems.push_back(ii+1);
	}
	permutations->insert(permutations->end(),
					lastGen.begin(), lastGen.end());

	for (unsigned int i = 2; i <= items.size(); ++i) {
		std::vector<std::vector<Item *> > gen;
		std::vector<typename std::vector<Item *>::iterator> rems;
		typename std::vector<std::vector<Item *> >::iterator gi;
		typename std::vector<typename std::vector<Item *>::iterator>::iterator ri;
		for (gi = lastGen.begin(), ri = lastRems.begin();
		gi != lastGen.end(); ++gi, ++ri) {
			for (typename std::vector<Item *>::iterator ii = *ri;
			ii != items.end(); ++ii) {
				std::vector<Item *> perm = *gi;
				perm.push_back(*ii);
				gen.push_back(perm);
				rems.push_back(ii+1);
			}
		}
		permutations->insert(permutations->end(), gen.begin(),
								gen.end());
		lastGen.swap(gen);
		lastRems.swap(rems);
	}
}
