#ifndef BCWAREHOUSE_H
#define BCWAREHOUSE_H

#include <vector>

#include "BoundaryCondition.h"

/**
 * Typedef to hide implementation details
 */
typedef std::vector<BoundaryCondition *>::iterator BCIterator;

class BCWarehouse
{
public:
  BCWarehouse();
  virtual ~BCWarehouse();

  BCIterator activeBCsBegin(unsigned int boundary_id);
  BCIterator activeBCsEnd(unsigned int boundary_id);

  BCIterator activeNodalBCsBegin(unsigned int boundary_id);
  BCIterator activeNodalBCsEnd(unsigned int boundary_id);

  void addBC(unsigned int boundary_id, BoundaryCondition *bc);
  void addNodalBC(unsigned int boundary_id, BoundaryCondition *bc);

  void activeBoundaries(std::set<short> & set_buffer) const;

protected:
  std::map<unsigned int, std::vector<BoundaryCondition *> > _active_bcs;
  std::map<unsigned int, std::vector<BoundaryCondition *> > _active_nodal_bcs;
};

#endif // BCWAREHOUSE_H
