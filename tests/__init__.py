from mock import patch


class PatchMixin(object):
    def _patch(self, target, *args, **kwargs):
        if isinstance(target, str):
            patcher = patch(target, *args, **kwargs)
        else:
            patcher = patch.object(target, *args, **kwargs)
        patched_entity = patcher.start()
        self.addCleanup(patcher.stop)
        return patched_entity
