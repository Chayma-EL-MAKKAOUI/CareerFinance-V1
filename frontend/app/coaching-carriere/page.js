import WorkingCareerCoaching from '../../components/CoachingCarriere/WorkingCareerCoaching';
<<<<<<< HEAD

export default function CoachingCarrierePage() {
  return <WorkingCareerCoaching />;
=======
import AuthGuard from '../../components/Auth/AuthGuard';

export default function CoachingCarrierePage() {
  return (
    <AuthGuard>
      <WorkingCareerCoaching />
    </AuthGuard>
  );
>>>>>>> 5e0de77 (Auth commit)
}